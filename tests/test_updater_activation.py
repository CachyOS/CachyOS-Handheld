"""Opt-in integration test using real user units and a fake Steam client.

Run with RUN_SYSTEMD_TESTS=1 python -m unittest discover -s tests -v.
Only the temporary test units and fixture directories are changed.
"""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest
import uuid

import vdf


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "usr/lib/cachyos-handheld/setup-steam-updater"
UNITS = ROOT / "usr/lib/systemd/user"


@unittest.skipUnless(os.environ.get("RUN_SYSTEMD_TESTS") == "1", "requires an active systemd user manager")
class ActivationTest(unittest.TestCase):
    def ctl(self, *args):
        return subprocess.run(["systemctl", "--user", *args], check=True, capture_output=True, text=True)

    def wait_for(self, predicate):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.05)
        self.fail("Timed out waiting for the registration service")

    def test_new_login_retries_confirmation_and_handles_two_accounts(self):
        with tempfile.TemporaryDirectory(prefix="cachyos-updater-test-") as temporary:
            base = Path(temporary)
            home = base / "home"
            home.mkdir()
            steam = home / "Steam"
            steam.mkdir()
            state = base / "state/cachyos-handheld/steam-updater"
            requests = base / "requests.json"
            selected = base / "selected"
            backend = base / "fake-add"
            backend.write_text(f'''#!{sys.executable}
import json
from pathlib import Path
import vdf
calls = Path({str(requests)!r})
account = Path({str(selected)!r}).read_text()
counts = json.loads(calls.read_text()) if calls.exists() else {{}}
counts[account] = counts.get(account, 0) + 1
calls.write_text(json.dumps(counts))
if counts[account] == 1:
    raise SystemExit(0)  # Accepted request that did not add anything.
path = Path({str(steam)!r}) / 'userdata' / account / 'config/shortcuts.vdf'
with path.open('rb') as stream:
    data = vdf.binary_load(stream)
data['shortcuts']['1'] = {{'AppName': 'Update CachyOS', 'Exe': '"/usr/bin/cachyos-handheld-update"'}}
path.write_bytes(vdf.binary_dumps(data))
''')
            backend.chmod(0o755)
            runner = base / "runner.py"
            runner.write_text(f'''
import importlib.machinery, importlib.util, sys
sys.dont_write_bytecode = True
from pathlib import Path
from unittest.mock import patch
loader = importlib.machinery.SourceFileLoader('registration', {str(SCRIPT)!r})
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
module.ADD_SHORTCUT_HELPER = {str(backend)!r}
module.CHECK_SECONDS = 0.05
module.RETRY_SECONDS = 0.2
module.SETUP_SECONDS = 3
with patch.object(Path, 'home', return_value=Path({str(home)!r})):
    raise SystemExit(module.main())
''')
            unit = "cachyos-updater-test-" + uuid.uuid4().hex
            runtime_units = Path(os.environ["XDG_RUNTIME_DIR"]) / "systemd/user"
            runtime_units.mkdir(parents=True, exist_ok=True)
            service_file = runtime_units / (unit + ".service")
            path_file = runtime_units / (unit + ".path")
            service = (UNITS / "cachyos-handheld-updater-setup.service").read_text()
            service = service.replace("ExecStart=/usr/lib/cachyos-handheld/setup-steam-updater",
                                      "ExecStart=" + shlex.join([sys.executable, str(runner)]))
            service = service.replace("/usr/share/applications/cachyos-handheld-update.desktop",
                                      str(ROOT / "usr/share/applications/cachyos-handheld-update.desktop"))
            service += f'\n[Service]\nEnvironment=XDG_STATE_HOME={base / "state"}\n'
            service_file.write_text(service)
            path_file.write_text((UNITS / "cachyos-handheld-updater-setup.path").read_text()
                                 .replace("%h", str(home)).replace("cachyos-handheld-updater-setup", unit))
            child = None
            try:
                self.ctl("daemon-reload")
                self.ctl("start", unit + ".path")
                home.joinpath(".steam").mkdir()
                home.joinpath(".steam/steam").symlink_to(steam)
                child = subprocess.Popen([
                    sys.executable, "-c",
                    'import ctypes,os,sys; '
                    'assert ctypes.CDLL(None).prctl(15,b"steam",0,0,0)==0; '
                    'print(os.getpid(),flush=True); sys.stdin.read()'
                ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
                home.joinpath(".steam/steam.pid").write_text(child.stdout.readline())
                self.wait_for(lambda: self.ctl("show", unit + ".service", "-p", "ActiveState", "--value").stdout.strip() == "activating")
                self.assertFalse(requests.exists())

                users = {}

                def login(account):
                    selected.write_text(str(account))
                    config = steam / "userdata" / str(account) / "config"
                    config.mkdir(parents=True, exist_ok=True)
                    shortcuts = config / "shortcuts.vdf"
                    shortcuts.write_bytes(vdf.binary_dumps({"shortcuts": {
                        "0": {"AppName": "Keep me", "Exe": '"/usr/bin/keep-me"'}}}))
                    steam.joinpath("config").mkdir(exist_ok=True)
                    users[str(76561197960265728 + account)] = {
                        "AccountName": f"account{account}", "Timestamp": str(int(time.time()))}
                    home.joinpath(".steam/registry.vdf").write_text(vdf.dumps({
                        "Registry": {"HKCU": {"Software": {"Valve": {"Steam": {
                            "AutoLoginUser": f"account{account}"}}}}}}))
                    steam.joinpath("config/loginusers.vdf").write_text(vdf.dumps({"users": users}))
                    self.wait_for(lambda: state.joinpath(f"{account}.json").exists()
                                  and json.loads(state.joinpath(f"{account}.json").read_text()).get("registered"))
                    with shortcuts.open("rb") as stream:
                        entries = vdf.binary_load(stream)["shortcuts"]
                    self.assertEqual(entries["0"]["AppName"], "Keep me")
                    self.assertEqual(len(entries), 2)
                    self.assertEqual(json.loads(requests.read_text())[str(account)], 2)
                    return shortcuts

                first = login(1)
                self.wait_for(lambda: self.ctl("show", unit + ".service", "-p", "ActiveState", "--value").stdout.strip() == "inactive")
                second = login(2)
                self.wait_for(lambda: self.ctl("show", unit + ".service", "-p", "ActiveState", "--value").stdout.strip() == "inactive")
                before = requests.read_bytes()
                # Simulate the user removing the shortcut, then another login event.
                second.write_bytes(vdf.binary_dumps({"shortcuts": {}}))
                steam.joinpath("config/loginusers.vdf").touch()
                time.sleep(0.5)
                self.assertEqual(requests.read_bytes(), before)
                self.ctl("stop", unit + ".path")
                start = self.ctl("show", unit + ".service", "-p", "ExecMainStartTimestampMonotonic", "--value").stdout
                steam.joinpath("config/loginusers.vdf").touch()
                time.sleep(0.5)
                self.assertEqual(self.ctl("show", unit + ".service", "-p", "ExecMainStartTimestampMonotonic", "--value").stdout, start)
                with first.open("rb") as stream:
                    self.assertEqual(len(vdf.binary_load(stream)["shortcuts"]), 2)
            finally:
                self.ctl("stop", unit + ".path", unit + ".service")
                if child is not None:
                    child.terminate()
                    child.communicate(timeout=5)
                service_file.unlink(missing_ok=True)
                path_file.unlink(missing_ok=True)
                self.ctl("daemon-reload")
