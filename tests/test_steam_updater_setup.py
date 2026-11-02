import importlib.machinery
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import vdf


SCRIPT = Path(__file__).resolve().parents[1] / "usr/lib/cachyos-handheld/setup-steam-updater"
LOADER = importlib.machinery.SourceFileLoader("setup_steam_updater", str(SCRIPT))
SPEC = importlib.util.spec_from_loader(LOADER.name, LOADER)
setup = importlib.util.module_from_spec(SPEC)
LOADER.exec_module(setup)


class RegistrationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.home = Path(temporary.name)
        self.root = self.home / "Steam library"
        self.root.joinpath("config").mkdir(parents=True)
        self.home.joinpath(".steam").mkdir()
        self.home.joinpath(".steam/steam").symlink_to(self.root)
        self.state = self.home / "state"
        self.state.mkdir()
        self.user(1, "first")
        self.select("first")
        self.client = patch.object(setup, "steam_process", return_value=("launch-one", 100))
        self.client.start()
        self.addCleanup(self.client.stop)
        self.request = patch.object(setup.subprocess, "run")
        self.run = self.request.start()
        self.addCleanup(self.request.stop)

    def write_vdf(self, path, data):
        path.write_text(vdf.dumps(data), encoding="utf-8")

    def user(self, account, name, timestamp="101"):
        path = self.root / "config/loginusers.vdf"
        users = vdf.loads(path.read_text())["users"] if path.exists() else {}
        users[str(setup.STEAM_ID_BASE + account)] = {"AccountName": name, "Timestamp": timestamp}
        self.write_vdf(path, {"users": users})
        self.root.joinpath("userdata", str(account), "config").mkdir(parents=True, exist_ok=True)

    def select(self, name):
        self.write_vdf(self.home / ".steam/registry.vdf", {
            "Registry": {"HKCU": {"Software": {"Valve": {"Steam": {"AutoLoginUser": name}}}}}
        })

    def shortcuts(self, account, entries):
        path = self.root / "userdata" / str(account) / "config/shortcuts.vdf"
        data = vdf.binary_dumps({"shortcuts": {str(i): entry for i, entry in enumerate(entries)}})
        path.write_bytes(data)
        return path

    def tick(self):
        setup.setup(self.home, self.state)

    def test_waits_for_a_login_in_this_steam_launch(self):
        self.user(1, "first", timestamp="99")
        self.tick()
        self.run.assert_not_called()
        self.user(1, "first", timestamp="101")
        self.tick()
        self.run.assert_called_once_with(
            ["/usr/bin/steamos-add-to-steam", setup.LAUNCHER], check=True, timeout=10)

    def test_waits_when_steam_is_not_running(self):
        with patch.object(setup, "steam_process", return_value=None):
            self.tick()
        self.run.assert_not_called()

    def test_requests_once_then_confirms_steams_own_database(self):
        other = self.shortcuts(1, [{"AppName": "Keep me", "Exe": '"/usr/bin/another-app"'}])
        original = other.read_bytes()
        self.tick()
        self.tick()
        self.run.assert_called_once()
        self.assertEqual(other.read_bytes(), original)
        self.assertFalse(json.loads(self.state.joinpath("1.json").read_text()).get("registered"))
        # Simulate Steam persisting the requested shortcut, not the setup helper.
        self.shortcuts(1, [{"Exe": f'"{setup.EXECUTABLE}"'}])
        self.tick()
        self.assertTrue(json.loads(self.state.joinpath("1.json").read_text())["registered"])
        self.run.assert_called_once()

    def test_existing_manual_shortcut_is_not_duplicated(self):
        self.shortcuts(1, [{"AppName": "Renamed updater", "Exe": setup.EXECUTABLE}])
        self.tick()
        self.run.assert_not_called()
        self.assertTrue(json.loads(self.state.joinpath("1.json").read_text())["registered"])

    def test_removed_registered_shortcut_stays_removed(self):
        path = self.shortcuts(1, [{"ShortcutPath": setup.LAUNCHER}])
        self.tick()
        path.unlink()
        self.tick()
        self.run.assert_not_called()

    def test_each_account_has_independent_registration(self):
        self.user(2, "second")
        self.shortcuts(1, [{"Exe": setup.EXECUTABLE}])
        self.tick()
        self.select("second")
        self.tick()
        self.assertTrue(self.state.joinpath("1.json").exists())
        self.assertTrue(self.state.joinpath("2.json").exists())
        self.run.assert_called_once()

    def test_account_change_before_request_defers_registration(self):
        with patch.object(setup, "active_account", side_effect=["1", "2"]):
            self.tick()
        self.run.assert_not_called()
        self.assertFalse(self.state.joinpath("1.json").exists())

    def test_failed_request_retries_without_marking_success(self):
        self.run.side_effect = subprocess.CalledProcessError(1, "steam")
        with self.assertRaises(subprocess.CalledProcessError):
            self.tick()
        self.assertFalse(self.state.joinpath("1.json").exists())
        self.run.side_effect = None
        self.tick()
        self.assertEqual(self.run.call_count, 2)

    def test_unconfirmed_request_retries_after_steam_restarts(self):
        self.tick()
        with patch.object(setup, "steam_process", return_value=("launch-two", 100)):
            self.tick()
        self.assertEqual(self.run.call_count, 2)

    def test_legacy_most_recent_login_is_supported(self):
        self.select("")
        self.write_vdf(self.root / "config/loginusers.vdf", {"users": {
            str(setup.STEAM_ID_BASE + 1): {"MostRecent": "1", "Timestamp": "101"}}})
        self.tick()
        self.run.assert_called_once()

    def test_corrupt_shortcuts_are_not_modified_or_added_to(self):
        path = self.shortcuts(1, [])
        path.write_bytes(b"invalid")
        with self.assertRaises(SyntaxError):
            self.tick()
        self.assertEqual(path.read_bytes(), b"invalid")
        self.run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
