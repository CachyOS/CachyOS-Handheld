import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "usr/bin/cachyos-handheld-update"


class UpdateLauncherTests(unittest.TestCase):
    def test_steam_libraries_are_removed_before_terminal_and_transaction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            capture = root / "environment"
            for command in ("konsole", "systemd-inhibit"):
                program = root / command
                program.write_text('#!/usr/bin/bash\n'
                                   'printf "%s|%s|%s" "${LD_PRELOAD-unset}" '
                                   '"${LD_LIBRARY_PATH-unset}" "$DISPLAY" > "$CAPTURE"\n'
                                   'exit 17\n')
                program.chmod(0o755)
            environment = dict(os.environ, PATH=f"{root}:/usr/bin", CAPTURE=str(capture),
                               DISPLAY=":99", LD_PRELOAD="/missing/steam-overlay.so",
                               LD_LIBRARY_PATH="/missing/steam-runtime")
            for arguments in ([], ["--run"]):
                result = subprocess.run(["bash", str(SCRIPT), *arguments], env=environment,
                                        input="\n", capture_output=True, text=True)
                self.assertEqual(result.returncode, 17)
                self.assertEqual(capture.read_text(), "unset|unset|:99")
                if arguments:
                    self.assertIn("exited with status 17", result.stdout)


if __name__ == "__main__":
    unittest.main()
