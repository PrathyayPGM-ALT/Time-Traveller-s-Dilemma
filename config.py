"""Global constants, palette and font helpers for Time Traveller's Dilemma."""

import pygame

WIDTH, HEIGHT = 1000, 800
FPS = 60
TITLE = "Time Traveller's Dilemma"

FONT_PATH = "fonts/IBMPlexMono-Regular.ttf"

# --- palette -------------------------------------------------------------
BLACK = (8, 8, 10)
NEAR_BLACK = (16, 16, 20)
WHITE = (235, 235, 235)
ASH = (150, 150, 158)        # narrator / faded memory
DIM = (84, 84, 96)
BLOOD = (150, 12, 12)        # the boss, danger
RIFT = (96, 206, 224)        # the void, time travel glow
WARN = (214, 168, 48)        # suspicion / time keepers
TITOR = (120, 224, 150)      # the green CRT terminal thread

# --- font cache ----------------------------------------------------------
_fonts = {}


def font(size):
    f = _fonts.get(size)
    if f is None:
        f = pygame.font.Font(FONT_PATH, size)
        _fonts[size] = f
    return f
