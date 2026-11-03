"""Run with RUN_SYSTEMD_TESTS=1; uses temporary user units and simulated Steam accounts."""

import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest

import vdf


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = Path(__file__).with_name("steam_fixture.py")
UNITS = ROOT / "usr/lib/systemd/user"


@unittest.skipUnless(os.environ.get("RUN_SYSTEMD_TESTS") == "1", "requires an active systemd user manager")
class ActivationTest(unittest.TestCase):
    def ctl(self, *args):
        return subprocess.run(["systemctl", "--user", *args], check=True, capture_output=True, text=True).stdout.strip()

    def wait_for(self, predicate):
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if predicate():
                return
            time.sleep(0.05)
        self.fail("Timed out waiting for the registration service")

    def wait_inactive(self):
        self.wait_for(lambda: self.ctl("show", self.unit + ".service", "-p", "ActiveState", "--value") == "inactive")

    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="cachyos-updater-test-")
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.home = self.base / "home"
        self.steam = self.home / "Steam"
        self.steam.mkdir(parents=True)
        self.requests = self.base / "requests.json"
        self.users = {}
        self.unit = self.base.name
        runtime = Path(os.environ["XDG_RUNTIME_DIR"]) / "systemd/user"
        runtime.mkdir(parents=True, exist_ok=True)
        self.addCleanup(self.ctl, "daemon-reload")
        for suffix in ("service", "path"):
            text = UNITS.joinpath(f"cachyos-handheld-updater-setup.{suffix}").read_text()
            text = text.replace("%h", str(self.home)).replace("cachyos-handheld-updater-setup", self.unit)
            if suffix == "service":
                text = text.replace("ExecStart=/usr/lib/cachyos-handheld/setup-steam-updater",
                                    "ExecStart=" + shlex.join([sys.executable, str(FIXTURE), "--setup"]))
                text = text.replace("/usr/share/applications/cachyos-handheld-update.desktop",
                                    str(ROOT / "usr/share/applications/cachyos-handheld-update.desktop"))
                text += f"\n[Service]\nEnvironment=CACHYOS_TEST_DIR={self.base}\nEnvironment=XDG_STATE_HOME={self.base / 'state'}\n"
            path = runtime / f"{self.unit}.{suffix}"
            path.write_text(text)
            self.addCleanup(path.unlink, missing_ok=True)
        self.addCleanup(self.ctl, "stop", self.unit + ".path", self.unit + ".service")
        self.ctl("daemon-reload")
        self.ctl("start", self.unit + ".path")

    def login(self, account):
        self.base.joinpath("selected").write_text(str(account))
        config = self.steam / "userdata" / str(account) / "config"
        config.mkdir(parents=True)
        shortcuts = config / "shortcuts.vdf"
        shortcuts.write_bytes(vdf.binary_dumps({"shortcuts": {
            "0": {"AppName": "Keep me", "Exe": '"/usr/bin/keep-me"'}}}))
        self.steam.joinpath("config").mkdir(exist_ok=True)
        self.users[str(76561197960265728 + account)] = {"AccountName": f"account{account}", "Timestamp": "101"}
        self.home.joinpath(".steam/registry.vdf").write_text(vdf.dumps({
            "Registry": {"HKCU": {"Software": {"Valve": {"Steam": {"AutoLoginUser": f"account{account}"}}}}}}))
        self.steam.joinpath("config/loginusers.vdf").write_text(vdf.dumps({"users": self.users}))
        marker = self.base / "state/cachyos-handheld/steam-updater" / f"{account}.json"
        self.wait_for(lambda: marker.exists() and json.loads(marker.read_text()).get("registered"))
        with shortcuts.open("rb") as stream:
            entries = vdf.binary_load(stream)["shortcuts"]
        self.assertEqual(entries["0"]["AppName"], "Keep me")
        self.assertEqual(len(entries), 2)
        self.assertEqual(json.loads(self.requests.read_text())[str(account)], 2)
        self.wait_inactive()
        return shortcuts

    def test_new_login_retries_confirmation_and_handles_two_accounts(self):
        self.home.joinpath(".steam").mkdir()
        self.home.joinpath(".steam/steam").symlink_to(self.steam)
        child = subprocess.Popen([sys.executable, str(FIXTURE), "--client"],
                                 stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        self.addCleanup(lambda: child.communicate(timeout=5))
        self.addCleanup(child.terminate)
        self.home.joinpath(".steam/steam.pid").write_text(child.stdout.readline())
        self.wait_for(lambda: self.ctl("show", self.unit + ".service", "-p", "ActiveState", "--value") == "activating")
        self.assertFalse(self.requests.exists())
        first, second = self.login(1), self.login(2)
        before = self.requests.read_bytes()
        second.write_bytes(vdf.binary_dumps({"shortcuts": {}}))
        login_file = self.steam / "config/loginusers.vdf"
        login_file.touch()
        time.sleep(0.5)
        self.wait_inactive()
        self.assertEqual(self.requests.read_bytes(), before)
        self.ctl("stop", self.unit + ".path")
        started = self.ctl("show", self.unit + ".service", "-p", "ExecMainStartTimestampMonotonic", "--value")
        login_file.touch()
        time.sleep(0.5)
        self.assertEqual(self.ctl("show", self.unit + ".service", "-p", "ExecMainStartTimestampMonotonic", "--value"), started)
        with first.open("rb") as stream:
            self.assertEqual(len(vdf.binary_load(stream)["shortcuts"]), 2)
