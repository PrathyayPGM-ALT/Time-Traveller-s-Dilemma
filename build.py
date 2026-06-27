"""Build a one-file Windows executable with PyInstaller.

Run:  python build.py
Output: dist/TimeTravellersDilemma.exe  (double-click to play; no Python needed)

Bundles the textures/fonts/sounds folders. The save file is written next to the
.exe at runtime so progress (and the persistent 'soul') survives.
"""

import os
import PyInstaller.__main__

SEP = os.pathsep   # ';' on Windows, ':' elsewhere

PyInstaller.__main__.run([
    "main.py",
    "--name", "TimeTravellersDilemma",
    "--onefile",
    "--windowed",
    "--noconfirm",
    "--clean",
    f"--add-data=textures{SEP}textures",
    f"--add-data=fonts{SEP}fonts",
    f"--add-data=sounds{SEP}sounds",
    # the game never imports these — keep the exe lean
    "--exclude-module", "numpy",
    "--exclude-module", "PIL",
])
