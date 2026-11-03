import importlib.machinery
import importlib.util
import json
import os
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
detect_steam_process = setup.steam_process


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
        self.client = self.enterContext(patch.object(setup, "steam_process", return_value="launch-one"))
        self.run = self.enterContext(patch.object(setup.subprocess, "run"))

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

    def tick(self, now=0):
        return setup.setup(self.home, self.state, now)

    def registered(self, account=1):
        return json.loads(self.state.joinpath(f"{account}.json").read_text()).get("registered", False)

    def test_saved_timestamps_do_not_block_automatic_login(self):
        self.user(1, "first", timestamp="99")
        self.tick()
        self.run.assert_called_once_with(
            ["/usr/bin/steamos-add-to-steam", setup.LAUNCHER], check=True, timeout=10)

    def test_waits_while_signed_out(self):
        self.select("")
        self.tick()
        self.run.assert_not_called()

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
        self.assertFalse(self.registered())
        self.shortcuts(1, [{"Exe": f'"{setup.EXECUTABLE}"'}])
        self.assertEqual(self.tick(setup.RETRY_SECONDS), "done")
        self.assertTrue(self.registered())
        self.run.assert_called_once()

    def test_existing_manual_shortcut_is_not_duplicated(self):
        self.shortcuts(1, [{"AppName": "Renamed updater", "Exe": setup.EXECUTABLE}])
        self.tick()
        self.run.assert_not_called()
        self.assertTrue(self.registered())

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
        with patch.object(setup, "active_account", side_effect=[("1", "101"), ("2", "101")]):
            self.tick()
        self.run.assert_not_called()
        self.assertFalse(self.state.joinpath("1.json").exists())

    def test_failed_request_retries_without_marking_success(self):
        self.run.side_effect = subprocess.CalledProcessError(1, "steam")
        with self.assertRaises(subprocess.CalledProcessError):
            self.tick()
        self.assertFalse(self.registered())
        self.run.side_effect = None
        self.tick(setup.RETRY_SECONDS)
        self.assertEqual(self.run.call_count, 2)

    def test_accepted_but_unconfirmed_request_retries_in_the_same_launch(self):
        self.tick()
        self.tick(setup.RETRY_SECONDS - 1)
        self.run.assert_called_once()
        self.tick(setup.RETRY_SECONDS)
        self.assertEqual(self.run.call_count, 2)
        self.shortcuts(1, [{"Exe": setup.EXECUTABLE}])
        self.assertEqual(self.tick(setup.RETRY_SECONDS + 1), "done")
        self.assertEqual(self.run.call_count, 2)

    def test_request_budget_is_bounded_and_resets_at_a_new_login(self):
        for attempt in range(setup.MAX_ATTEMPTS):
            self.tick(attempt * setup.RETRY_SECONDS)
        self.assertEqual(self.tick(setup.MAX_ATTEMPTS * setup.RETRY_SECONDS), "exhausted")
        self.tick(1000)
        self.assertEqual(self.run.call_count, setup.MAX_ATTEMPTS)
        self.user(1, "first", timestamp="102")
        self.tick(1001)
        self.assertEqual(self.run.call_count, setup.MAX_ATTEMPTS + 1)

    def test_missing_login_files_can_appear_during_the_bounded_window(self):
        login_file = self.root / "config/loginusers.vdf"
        login_file.unlink()
        clock = [0]

        def advance(seconds):
            clock[0] += seconds
            if not login_file.exists():
                self.user(1, "first")
            elif self.run.called:
                self.shortcuts(1, [{"Exe": setup.EXECUTABLE}])

        with patch.object(setup.time, "monotonic", side_effect=lambda: clock[0]), \
             patch.object(setup.time, "sleep", side_effect=advance):
            setup.register(self.home, self.state)
        self.run.assert_called_once()
        self.assertTrue(self.registered())

    def test_waiting_for_authentication_has_a_deadline(self):
        self.select("")
        clock = [0]
        with patch.object(setup.time, "monotonic", side_effect=lambda: clock[0]), \
             patch.object(setup.time, "sleep", side_effect=lambda seconds: clock.__setitem__(0, clock[0] + seconds)):
            setup.register(self.home, self.state)
        self.run.assert_not_called()
        self.assertGreaterEqual(clock[0], setup.SETUP_SECONDS)
        self.assertLess(clock[0], setup.SETUP_SECONDS + setup.CHECK_SECONDS)

    def test_real_process_detection_ignores_an_unrelated_pid(self):
        self.client.side_effect = detect_steam_process
        self.home.joinpath(".steam/steam.pid").write_text(str(os.getpid()))
        self.assertEqual(self.tick(), "idle")
        self.run.assert_not_called()

    def test_unconfirmed_request_retries_after_steam_restarts(self):
        self.tick()
        with patch.object(setup, "steam_process", return_value="launch-two"):
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
