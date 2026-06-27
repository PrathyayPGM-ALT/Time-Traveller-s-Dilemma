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

_FROZEN = getattr(sys, "frozen", False)
if _FROZEN:
    os.chdir(sys._MEIPASS)

import pygame

import scene
if _FROZEN:
    scene.SAVE_PATH = os.path.join(os.path.dirname(sys.executable), "save.json")

from scene import Game
from flow import (TitleScene, IntroScene, TrappedScene, EndingScene,
                  AchievementsScene)
from hub import HubScene
from troi import TroiScene
from era import EraScene
from training import TrainingScene


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


asyncio.run(main())
