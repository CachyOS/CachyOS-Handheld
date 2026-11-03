#!/usr/bin/python
"""Subprocess stand-ins for the systemd activation test."""

import ctypes
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import sys
from unittest.mock import patch

import vdf


if sys.argv[1] == "--client":
    assert ctypes.CDLL(None).prctl(15, b"steam", 0, 0, 0) == 0
    print(os.getpid(), flush=True)
    sys.stdin.read()
    sys.exit(0)

base = Path(os.environ["CACHYOS_TEST_DIR"])
if sys.argv[1] == "--setup":
    sys.dont_write_bytecode = True
    script = Path(__file__).resolve().parents[1] / "usr/lib/cachyos-handheld/setup-steam-updater"
    loader = importlib.machinery.SourceFileLoader("registration", str(script))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    setup = importlib.util.module_from_spec(spec)
    loader.exec_module(setup)
    setup.ADD_SHORTCUT_HELPER = str(Path(__file__).resolve())
    setup.CHECK_SECONDS, setup.RETRY_SECONDS, setup.SETUP_SECONDS = 0.05, 0.2, 3
    with patch.object(Path, "home", return_value=base / "home"):
        sys.exit(setup.main())

account = base.joinpath("selected").read_text()
requests = base / "requests.json"
counts = json.loads(requests.read_text()) if requests.exists() else {}
counts[account] = counts.get(account, 0) + 1
requests.write_text(json.dumps(counts))
if counts[account] == 1:
    sys.exit(0)  # Accept the first request without saving it, to exercise retries.
shortcuts = base / "home/Steam/userdata" / account / "config/shortcuts.vdf"
with shortcuts.open("rb") as stream:
    data = vdf.binary_load(stream)
data["shortcuts"]["1"] = {"AppName": "Update CachyOS", "Exe": '"/usr/bin/cachyos-handheld-update"'}
shortcuts.write_bytes(vdf.binary_dumps(data))
