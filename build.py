"""Build a native, no-Python-needed executable with PyInstaller.

Run:  python build.py

Output depends on the OS you run it on (PyInstaller can only build for the
platform it runs on — you cannot make a Mac .app on Windows):
  Windows -> dist/TimeTravellersDilemma.exe   (single file, double-click)
  macOS   -> dist/TimeTravellersDilemma.app   (app bundle)
  Linux   -> dist/TimeTravellersDilemma       (single file)

Bundles the textures/fonts/sounds folders. The save file is written next to the
program at runtime so progress (and the persistent 'soul') survives.
"""

import os
import sys
import PyInstaller.__main__

SEP = os.pathsep   # ';' on Windows, ':' elsewhere
MACOS = sys.platform == "darwin"

opts = [
    "main.py",
    "--name", "TimeTravellersDilemma",
    "--windowed",
    "--noconfirm",
    "--clean",
    f"--add-data=textures{SEP}textures",
    f"--add-data=fonts{SEP}fonts",
    f"--add-data=sounds{SEP}sounds",
    # the game never imports these — keep the build lean
    "--exclude-module", "numpy",
    "--exclude-module", "PIL",
]

# Single-file binary on Windows/Linux. On macOS a one-dir build makes a cleaner,
# more reliable .app bundle, so skip --onefile there.
if not MACOS:
    opts.insert(3, "--onefile")

PyInstaller.__main__.run(opts)
