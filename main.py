"""Time Traveller's Dilemma — entry point.

Wires the scenes together and starts the game at the title screen.
Run from source with:  python main.py
Build a Windows .exe with: python build.py       (see build.py)
Build a web (browser) build with: python build_web.py   (uses pygbag)

The loop is async so the very same main.py runs both natively and under
pygbag (CPython compiled to WebAssembly), which needs the loop to yield to
the browser each frame.
"""

import asyncio
import os
import sys

# When running from a PyInstaller bundle, assets (textures/fonts/sounds) live in
# the temporary extraction dir; read from there, but keep the save file next to
# the .exe so the persistent "soul" survives between sessions.
_FROZEN = getattr(sys, "frozen", False)
if _FROZEN:
    os.chdir(sys._MEIPASS)

# Import pygame directly in the entry file. pygbag scans main.py to decide which
# packages to set up for the web build; if it doesn't see `import pygame` here,
# it never initialises pygame and `import pygame` elsewhere yields a stub with no
# .init() (grey-screen hang in the browser). Harmless on desktop.
import pygame  # noqa: E402,F401

import scene  # noqa: E402
if _FROZEN:
    scene.SAVE_PATH = os.path.join(os.path.dirname(sys.executable), "save.json")

from scene import Game  # noqa: E402
from flow import (TitleScene, IntroScene, TrappedScene, EndingScene,  # noqa: E402
                  AchievementsScene)
from hub import HubScene  # noqa: E402
from troi import TroiScene  # noqa: E402
from era import EraScene  # noqa: E402
from training import TrainingScene  # noqa: E402


async def main():
    print("BOOT: main() entered")
    game = Game()
    game.register("title", TitleScene)
    game.register("intro", IntroScene)
    game.register("hub", HubScene)
    game.register("troi", TroiScene)
    game.register("era", EraScene)
    game.register("training", TrainingScene)
    game.register("trapped", TrappedScene)
    game.register("ending", EndingScene)
    game.register("achievements", AchievementsScene)
    print("BOOT: entering main loop")
    await game.run("title")


# NOTE: called unconditionally, NOT under `if __name__ == "__main__"`.
# pygbag (web/WASM) *sources* this file under a name other than "__main__", so a
# guard would mean main() never runs and the game hangs on a grey screen. Native
# runs (python main.py, the PyInstaller exe) execute this top-level too, which is
# exactly what we want. Nothing imports this module, so this is safe.
asyncio.run(main())
