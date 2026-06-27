"""Procedurally generate ALL the game's pixel art.

Sprites are authored as pixel grids + palettes, then scaled (nearest-neighbour)
to their in-game footprints. Props go to textures/props/ (picked up by the
drop-in system in world.py); characters overwrite textures/ (originals are
backed up to textures/_original/ once).

Run:  python make_art.py
"""

import os
import shutil

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

import worldgen

pygame.init()
pygame.display.set_mode((1, 1))

TEX = "textures"
PROPS_DIR = os.path.join(TEX, "props")
BACKUP = os.path.join(TEX, "_original")


def grid(rows, pal, t="."):
    h = len(rows)
    w = max(len(r) for r in rows)
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch != t and ch in pal:
                s.set_at((x, y), pal[ch])
    return s


def scaled(s, size):
    return pygame.transform.scale(s, size)


OL = (32, 26, 24)

PROPS = {}

PROPS["crate"] = ([
    "..DDDDDDDDDD..",
    ".DLLLLLLLLLLD.",
    ".DLBBBBBBBBLD.",
    ".DBbBBBBBBbBD.",
    ".DBBbBBBBbBBD.",
    ".DBBBbBBbBBBD.",
    ".DBBBBbbBBBBD.",
    ".DBBBBbbBBBBD.",
    ".DBBBbBBbBBBD.",
    ".DBBbBBBBbBBD.",
    ".DBbBBBBBBbBD.",
    ".DBBBBBBBBBBD.",
    ".DLLLLLLLLLLD.",
    "..DDDDDDDDDD..",
], {"D": OL, "B": (124, 82, 44), "b": (92, 60, 32), "L": (156, 112, 68)})

PROPS["barrel"] = ([
    "..DDDDDDDD..",
    ".DLLLLLLLLD.",
    ".DBBBBBBBBD.",
    ".DKKKKKKKKD.",
    ".DBBBBBBBBD.",
    ".DBBBBBBBBD.",
    ".DKKKKKKKKD.",
    ".DBBBBBBBBD.",
    ".DBBBBBBBBD.",
    ".DKKKKKKKKD.",
    ".DBBBBBBBBD.",
    ".DLLLLLLLLD.",
    "..DDDDDDDD..",
], {"D": OL, "B": (120, 80, 44), "L": (156, 112, 68), "K": (74, 50, 28)})

PROPS["plant"] = ([
    "............",
    "....GG......",
    "...GgGG.....",
    "..GGGgGG....",
    ".GGgGGGgG...",
    ".GGGGgGGG...",
    "..GGGgGG....",
    "...GGGG.....",
    "....GG......",
    "....pp......",
    "...DPPD.....",
    "...DPPD.....",
    "...DppD.....",
    "...DDDD.....",
], {"G": (64, 150, 84), "g": (40, 110, 60), "P": (120, 76, 44), "p": (88, 56, 32), "D": OL})

PROPS["tree"] = ([
    "....GG......",
    "...GGGG.....",
    "..GGggGG....",
    ".GGGGGGGG...",
    ".GGggGGgG...",
    ".GGGGGGGG...",
    "..GGGgGG....",
    "...GGGG.....",
    "....BB......",
    "....BB......",
    "....bb......",
    "....BB......",
    "...DDDD.....",
], {"G": (60, 140, 78), "g": (40, 104, 56), "B": (96, 66, 40), "b": (70, 48, 28), "D": OL})

PROPS["candle"] = ([
    "....ff....",
    "...fFFf...",
    "...fFFf...",
    "....FF....",
    "....DD....",
    "...DWWD...",
    "...DWWD...",
    "...DWWD...",
    "...DwwD...",
    "...DWWD...",
    "...DWWD...",
    "..DHHHHD..",
    "..DHHHHD..",
    "..DDDDDD..",
], {"f": (255, 240, 180), "F": (250, 180, 70), "D": OL, "W": (224, 212, 182),
    "w": (180, 168, 140), "H": (120, 120, 132)})

PROPS["crt"] = ([
    "................",
    ".DDDDDDDDDDDDDD..",
    ".DCCCCCCCCCCCCD..",
    ".DCSSSSSSSSSSCD..",
    ".DCSggggggggSCD..",
    ".DCSSSSSSSSSSCD..",
    ".DCSggggggggSCD..",
    ".DCSSSSSSSSSSCD..",
    ".DCSggggggggSCD..",
    ".DCSSSSSSSSSSCD..",
    ".DCCCCCCCCCCCCD..",
    ".DDDDDDDDDDDDDD..",
    "....DDDDDD......",
    "...DCCCCCCD.....",
    "..DDDDDDDDDD....",
], {"D": OL, "C": (58, 58, 64), "S": (16, 34, 24), "g": (96, 206, 150)})

PROPS["computer"] = ([
    "..................",
    ".DDDDDDDDDDDDDDDD..",
    ".DBBBBBBBBBBBBBBD..",
    ".DBSSSSSSSSSSSSBD..",
    ".DBSggggggggggSBD..",
    ".DBSSSSSSSSSSSSBD..",
    ".DBBBBBBBBBBBBBBD..",
    ".DDDDDDDDDDDDDDDD..",
    "..DBBBBBBBBBBBBD...",
    "..DBkBkBkBkBkBBD...",
    "..DBBBBBBBBBBBBD...",
    "..DDDDDDDDDDDDDD...",
], {"D": OL, "B": (206, 198, 178), "S": (40, 60, 52), "g": (96, 206, 224), "k": (120, 116, 104)})

PROPS["server"] = ([
    "DDDDDDDDDDDD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKgCD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKKCD",
    "DCKKKKKKKrCD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKgCD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKKCD",
    "DCKKKKKKKgCD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKrCD",
    "DCCCCCCCCCCD",
    "DCKKKKKKKgCD",
    "DCCCCCCCCCCD",
    "DCCCCCCCCCCD",
    "DDDDDDDDDDDD",
], {"D": OL, "C": (54, 54, 60), "K": (28, 28, 32), "g": (0, 220, 120), "r": (200, 60, 40)})

PROPS["shelf"] = ([
    "DDDDDDDDDDDDDDDD",
    "DWWWWWWWWWWWWWWD",
    "DWrWgWbWyWrWgWWD",
    "DWWWWWWWWWWWWWWD",
    "DDDDDDDDDDDDDDDD",
    "DWWWWWWWWWWWWWWD",
    "DWgWbWyWrWgWbWWD",
    "DWWWWWWWWWWWWWWD",
    "DDDDDDDDDDDDDDDD",
    "DWWWWWWWWWWWWWWD",
    "DWbWyWrWgWbWyWWD",
    "DWWWWWWWWWWWWWWD",
    "DDDDDDDDDDDDDDDD",
], {"D": OL, "W": (96, 72, 48), "r": (160, 70, 60), "g": (80, 130, 90),
    "b": (70, 100, 150), "y": (170, 150, 70)})

PROPS["bookshelf"] = ([
    "DDDDDDDDDDDDDDDD",
    "DWWWWWWWWWWWWWWD",
    "DWrGbYrGbYrGbWD",
    "DWrGbYrGbYrGbWD",
    "DWrGbYrGbYrGbWD",
    "DWWWWWWWWWWWWWWD",
    "DWbYrGbYrGbYrWD",
    "DWbYrGbYrGbYrWD",
    "DWbYrGbYrGbYrWD",
    "DWWWWWWWWWWWWWWD",
    "DWGbYrGbYrGbYWD",
    "DWGbYrGbYrGbYWD",
    "DWGbYrGbYrGbYWD",
    "DWWWWWWWWWWWWWWD",
    "DDDDDDDDDDDDDDDD",
], {"D": OL, "W": (88, 66, 44), "r": (160, 70, 60), "G": (80, 130, 90),
    "b": (70, 100, 150), "Y": (170, 150, 70)})

PROPS["table"] = ([
    "DDDDDDDDDDDDDDDDDDDD",
    "DLLLLLLLLLLLLLLLLLLD",
    "DLTTTTTTTTTTTTTTTTLD",
    "DLTtTTTtTTTtTTTtTTLD",
    "DLTTTTTTTTTTTTTTTTLD",
    "DLTTtTTTtTTTtTTTtTLD",
    "DLTTTTTTTTTTTTTTTTLD",
    "DLLLLLLLLLLLLLLLLLLD",
    "DDDDDDDDDDDDDDDDDDDD",
    "..GG..........GG....",
    "..DD..........DD....",
], {"D": OL, "L": (140, 104, 70), "T": (112, 80, 52), "t": (90, 62, 38), "G": (80, 58, 38)})

PROPS["chair"] = ([
    "DDDDDDDD",
    "DCCCCCCD",
    "DCccccCD",
    "DCCCCCCD",
    "DDDDDDDD",
    ".G....G.",
    ".G....G.",
    ".D....D.",
], {"D": OL, "C": (110, 80, 54), "c": (88, 62, 40), "G": (70, 50, 32)})

PROPS["pillar"] = ([
    "DDDDDDDDD",
    "DLLLLLLLD",
    "DDDDDDDDD",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    ".DSsSsSD.",
    ".DSSSSSD.",
    "DDDDDDDDD",
    "DLLLLLLLD",
    "DDDDDDDDD",
], {"D": OL, "S": (120, 120, 130), "s": (92, 92, 102), "L": (150, 150, 162)})

PROPS["telescope"] = ([
    "................",
    "...........gg...",
    "..........tTTt..",
    ".........tTTt...",
    "........tTTt....",
    ".......tTTt.....",
    "......tTTt......",
    ".....tTTt.......",
    "....mTTt........",
    "....mm..........",
    "...DmmD.........",
    "..D.mm..D.......",
    ".D..mm...D......",
    "D...DD....D.....",
    "D...DD....D.....",
], {"D": OL, "T": (120, 120, 132), "t": (86, 86, 96), "g": (214, 168, 48), "m": (74, 74, 84)})

PROPS["rubble"] = ([
    "................",
    "...DD....DDD....",
    "..DSSD..DSSSD...",
    ".DSSSSD.DSssSD..",
    ".DSssSDDSSSSSD..",
    "DSSSSSSDSSssSD..",
    "DSssSSSDDSSSDD..",
    "DSSSSSDD.DDD....",
    ".DDDDD..........",
], {"D": OL, "S": (94, 90, 96), "s": (66, 64, 70)})

PROPS["monument"] = ([
    "....DDDD....",
    "...DLLLLD...",
    "...DSSSSD...",
    "..DSSSSSSD..",
    "..DSiiiiSD..",
    "..DSSSSSSD..",
    "..DSiiiiSD..",
    "..DSSSSSSD..",
    "..DSiiiiSD..",
    "..DSSSSSSD..",
    "..DSiiiiSD..",
    "..DSSSSSSD..",
    "..DSiiiiSD..",
    "..DSSSSSSD..",
    ".DSSSSSSSSD.",
    "DDDDDDDDDDDD",
    "DLLLLLLLLLLD",
    "DDDDDDDDDDDD",
], {"D": OL, "S": (104, 104, 114), "i": (140, 140, 150), "L": (140, 140, 152)})

PROPS["stalagmite"] = ([
    "....DD....",
    "....SS....",
    "...DSSD...",
    "...SSSS...",
    "...SssS...",
    "..DSSSSD..",
    "..SSSSSS..",
    "..SSssSS..",
    ".DSSSSSSD.",
    ".SSSSSSSS.",
    ".SSSssSSS.",
    "DSSSSSSSSD",
    "SSSSSSSSSS",
    "SSSSssSSSS",
    "DDDDDDDDDD",
], {"D": OL, "S": (92, 74, 58), "s": (66, 52, 40)})

PROPS["poster"] = ([
    "DDDDDDDDDDDDDD",
    "DPPPPPPPPPPPPD",
    "DPTTTTTTTTTTPD",
    "DPPPPPPPPPPPPD",
    "DPllllllllllPD",
    "DPllllllllllPD",
    "DPPPPPPPPPPPPD",
    "DPllllllllllPD",
    "DPllllllllllPD",
    "DPPPPPPPPPPPPD",
    "DPllllllllllPD",
    "DPllllllPPPPPD",
    "DPPPPPPPPPPPPD",
    "DDDDDDDDDDDDDD",
], {"D": OL, "P": (200, 196, 180), "T": (150, 70, 64), "l": (120, 120, 126)})

PROPS["payphone"] = ([
    "DDDDDDDDDDDD",
    "DCCCCCCCCCCD",
    "DCSSSSSSSSCD",
    "DCSssssssSCD",
    "DCSSSSSSSSCD",
    "DCCCCCCCCCCD",
    "DCHHHHHHHHCD",
    "DChhhhhhhhCD",
    "DCCCCCCCCCCD",
    "DCkCkCkCkCCD",
    "DCkCkCkCkCCD",
    "DCkCkCkCkCCD",
    "DCCCCCCCCCCD",
    "DCCCCCCCCCCD",
    "DDDDDDDDDDDD",
], {"D": OL, "C": (48, 58, 68), "S": (24, 28, 32), "s": (60, 70, 80),
    "H": (120, 130, 140), "h": (80, 88, 96), "k": (96, 104, 114)})

PROPS["desk"] = ([
    "DDDDDDDDDDDDDDDDDDDD",
    "DLLLLLLLLLLLLLLLLLLD",
    "DTTTTTTTTTTTTTTTTTTD",
    "DTTTTDDDDTTTTTTTTTTD",
    "DTTTTDppDTTTTTTTTTTD",
    "DTTTTDDDDTTTTTTTTTTD",
    "DTTTTTTTTTTTTTTTTTTD",
    "DDDDDDDDDDDDDDDDDDDD",
    ".G................G.",
    ".D................D.",
], {"D": OL, "L": (140, 104, 70), "T": (112, 80, 52), "p": (70, 50, 32), "G": (80, 58, 38)})

PROPS["core"] = ([
    "....DDDDDD....",
    "...DKKKKKKD...",
    "..DKKKKKKKKD..",
    "..DKrrrrrrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrRRRRrKD..",
    "..DKrrrrrrKD..",
    "..DKKKKKKKKD..",
    "...DKKKKKKD...",
    "....DDDDDD....",
], {"D": OL, "K": (28, 14, 16), "r": (150, 18, 18), "R": (224, 64, 64)})

PROPS["console"] = ([
    "DDDDDDDDDDDDDDDD",
    "DCCCCCCCCCCCCCCD",
    "DCSSSSSSSSSSSSCD",
    "DCSggggggggggSCD",
    "DCSSSSSSSSSSSSCD",
    "DCCCCCCCCCCCCCCD",
    "DCkCkCkCkCkCkCCD",
    "DCCCCCCCCCCCCCCD",
    "DCkCkCkCkCkCkCCD",
    "DCCCCCCCCCCCCCCD",
    "DCgCgCgCgCgCgCCD",
    "DCCCCCCCCCCCCCCD",
    "DDDDDDDDDDDDDDDD",
], {"D": OL, "C": (40, 46, 52), "S": (20, 28, 34), "g": (96, 206, 224), "k": (74, 82, 92)})

PROPS["fire"] = ([
    "..............",
    ".....ff.......",
    "....fFFf......",
    "...fFOOFf.....",
    "..fFOOOOFf....",
    "..fFOyyOFf....",
    "..fFOyyyOf....",
    "...fOyyOO.....",
    "....FOOF......",
    "..LLLDDLLL....",
    ".LbLbLbLbL....",
    "..DDDDDDDD....",
], {"f": (250, 140, 50), "F": (250, 170, 70), "O": (250, 196, 96),
    "y": (255, 236, 168), "L": (96, 68, 42), "b": (70, 48, 28), "D": OL})

PROPS["painting"] = ([
    "DDDDDDDDDDDDDDDDDDDDDD",
    "DWWWWWWWWWWWWWWWWWWWWD",
    "DWWWWWWoooooWWWWWWWWWD",
    "DWWWWooWWWWWooWWWWWWWD",
    "DWWWoWWWWWWWWWoWWWWWWD",
    "DWWoWWWoooWWWWWoWWWWWD",
    "DWWoWWoWWWoWWWWoWWWWWD",
    "DWWoWWoWoWoWWWoWWWWWWD",
    "DWWoWWoWWooWWoWWWWWWWD",
    "DWWoWWoooWWWooWWWWWWWD",
    "DWWWoWWWWWoooWWWWWWWWD",
    "DWWWWoooooWWWWWWWWWWWD",
    "DWWWWWWWWWWWWWWWWWWWWD",
    "DWWWiWiWiWiWiWiWiWWWWD",
    "DDDDDDDDDDDDDDDDDDDDDD",
], {"D": OL, "W": (58, 46, 38), "o": (184, 92, 42), "i": (128, 96, 64)})

PROPS["cot"] = ([
    "DDDDDDDDDDDDDDDDDDDDDD",
    "DPPPPPPDFFFFFFFFFFFFFD",
    "DPPPPPPDFFFFFFFFFFFFFD",
    "DPPPPPPDFFFFFFFFFFFFFD",
    "DWWWWWWWWWWWWWWWWWWWWD",
    "DDDDDDDDDDDDDDDDDDDDDD",
    ".G..................G.",
    ".D..................D.",
], {"D": OL, "P": (188, 188, 200), "F": (92, 72, 110), "W": (72, 54, 44), "G": (60, 44, 32)})

def _lighten(c, d=26):
    return tuple(min(255, v + d) for v in c)


def _darken(c, d=22):
    return tuple(max(0, v - d) for v in c)


def player_pal(coat):
    return {"D": (16, 14, 18), "H": (52, 48, 58), "h": (32, 30, 40),
            "S": (192, 180, 172), "s": (150, 136, 132), "E": (18, 16, 22),
            "e": (154, 168, 176), "m": (74, 46, 48),
            "L": _lighten(coat), "R": coat, "r": _darken(coat),
            "P": (64, 66, 82), "p": (46, 48, 60), "K": (44, 42, 52)}


PL = (116, 56, 54)

PLAYER_DOWN_1 = ([
    "................",
    "....DHHHHD......",
    "...DHHHHHhD.....",
    "...DHSSSShD.....",
    "...DEesseED.....",
    "...DsSssSsD.....",
    "...DSsmmsSD.....",
    "....DSSSD.......",
    "...DLRRRRrD.....",
    "..DLRRRRRRrD....",
    "..DSRRRRRRSD....",
    "...DLRRRRrD.....",
    "...DLRRRRrD.....",
    "...DPPPPPPD.....",
    "...DPPDDPPD.....",
    "...DKKDDKKD.....",
], player_pal(PL))

PLAYER_DOWN_2 = ([
    "................",
    "....DHHHHD......",
    "...DHHHHHhD.....",
    "...DHSSSShD.....",
    "...DEesseED.....",
    "...DsSssSsD.....",
    "...DSsmmsSD.....",
    "....DSSSD.......",
    "...DLRRRRrD.....",
    "..DLRRRRRRrD....",
    "..DSRRRRRRSD....",
    "...DLRRRRrD.....",
    "...DLRRRRrD.....",
    "...DPPPPPPD.....",
    "...DPPDDPPD.....",
    "....DKKKKD......",
], player_pal(PL))

PLAYER_UP_1 = ([
    "................",
    "....DHHHHD......",
    "...DHHHHHhD.....",
    "...DHHHHHHD.....",
    "...DHhhhhHD.....",
    "...DHHHHHHD.....",
    "...DHHHHHhD.....",
    "....DHHHD.......",
    "...DLRRRRrD.....",
    "..DLRRRRRRrD....",
    "..DSRRRRRRSD....",
    "...DLRRRRrD.....",
    "...DLRRRRrD.....",
    "...DPPPPPPD.....",
    "...DPPDDPPD.....",
    "...DKKDDKKD.....",
], player_pal(PL))

PLAYER_UP_2 = ([
    "................",
    "....DHHHHD......",
    "...DHHHHHhD.....",
    "...DHHHHHHD.....",
    "...DHhhhhHD.....",
    "...DHHHHHHD.....",
    "...DHHHHHhD.....",
    "....DHHHD.......",
    "...DLRRRRrD.....",
    "..DLRRRRRRrD....",
    "..DSRRRRRRSD....",
    "...DLRRRRrD.....",
    "...DLRRRRrD.....",
    "...DPPPPPPD.....",
    "...DPPDDPPD.....",
    "....DKKKKD......",
], player_pal(PL))

PLAYER_SIDE_1 = ([
    "................",
    "...DHHHHD.......",
    "..DHHHHHhD......",
    "..DHHSSShD......",
    "..DHSEeSHD......",
    "..DHSssmD.......",
    "...DDSSDD.......",
    "...DSSD.........",
    "...DLRRrD.......",
    "..DLRRRRSD......",
    "..DLRRRrD.......",
    "...DLRrD........",
    "...DPPPPD.......",
    "...DPPPPD.......",
    "...DPPDPPD......",
    "...DKKDKKD......",
], player_pal(PL))

PLAYER_SIDE_2 = ([
    "................",
    "...DHHHHD.......",
    "..DHHHHHhD......",
    "..DHHSSShD......",
    "..DHSEeSHD......",
    "..DHSssmD.......",
    "...DDSSDD.......",
    "...DSSD.........",
    "...DLRRrD.......",
    "..DLRRRRSD......",
    "..DLRRRrD.......",
    "...DLRrD........",
    "...DPPPPD.......",
    "...DPPPPD.......",
    "...DPPDPPD......",
    "..DKKDDKK.......",
], player_pal(PL))


def npc_grid(coat, hair):
    return ([
        "................",
        "....DHHHHD......",
        "...DHHHHHhD.....",
        "...DHSSSShD.....",
        "...DSEEEESD.....",
        "...DsSssSsD.....",
        "...DSssssSD.....",
        "....DSSSD.......",
        "...DLCCCcD......",
        "..DLCCCCCcD.....",
        "..DSCCCCCSD.....",
        "...DLCCCcD......",
        "...DLCCCcD......",
        "...DLCCCcD......",
        "...DKKDDKKD.....",
        "................",
    ], {"D": (18, 16, 22), "H": hair, "h": (30, 28, 34),
        "S": (182, 172, 166), "s": (140, 130, 128), "E": (14, 12, 18),
        "L": _lighten(coat), "C": coat, "c": _darken(coat), "K": (32, 30, 38)})


NPCS = {
    "npc1": npc_grid((66, 78, 104), (40, 38, 44)),
    "npc2": npc_grid((92, 88, 72), (34, 32, 30)),
    "npc3": npc_grid((70, 96, 92), (46, 42, 40)),
}

BOSS = ([
    "................",
    "......DDDD......",
    ".....DKKKKD.....",
    ".....DKKKKD.....",
    ".....DKKKKD.....",
    ".....DKrrKD.....",
    ".....DKKKKD.....",
    ".....DKKKKD.....",
    "....DDKKKKDD....",
    "...DKKKKKKKKD...",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "..DKKKKKKKKKKD..",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "...DKKKKKKKKD...",
    "....DKKKKKKD....",
    "....DKKKKKKD....",
    "....DKKKKKKD....",
    "....DK..KKD.....",
    "....DK..KKD.....",
    "....DKKKKKKD....",
    "....DDDDDDDD....",
], {"D": (8, 6, 10), "K": (22, 20, 28), "r": (175, 32, 32)})


def main():
    os.makedirs(PROPS_DIR, exist_ok=True)
    os.makedirs(BACKUP, exist_ok=True)

    for kind, (rows, pal) in PROPS.items():
        fp = worldgen.PROP_SIZE.get(kind, (70, 70))
        pygame.image.save(scaled(grid(rows, pal), fp),
                          os.path.join(PROPS_DIR, kind + ".png"))
    print(f"props: {len(PROPS)} -> {PROPS_DIR}\\")

    def save_char(name, surf):
        dst = os.path.join(TEX, name + ".png")
        bak = os.path.join(BACKUP, name + ".png")
        if os.path.exists(dst) and not os.path.exists(bak):
            shutil.copy2(dst, bak)
        pygame.image.save(surf, dst)

    psize = (48, 48)
    s1 = scaled(grid(*PLAYER_SIDE_1), psize)
    s2 = scaled(grid(*PLAYER_SIDE_2), psize)
    save_char("player_down_1", scaled(grid(*PLAYER_DOWN_1), psize))
    save_char("player_down_2", scaled(grid(*PLAYER_DOWN_2), psize))
    save_char("player_up_1", scaled(grid(*PLAYER_UP_1), psize))
    save_char("player_up_2", scaled(grid(*PLAYER_UP_2), psize))
    save_char("player_right_1", s1)
    save_char("player_right_2", s2)
    save_char("player_left_1", pygame.transform.flip(s1, True, False))
    save_char("player_left_2", pygame.transform.flip(s2, True, False))

    for name, (rows, pal) in NPCS.items():
        save_char(name, scaled(grid(rows, pal), (48, 48)))

    save_char("boss", scaled(grid(*BOSS), (160, 320)))
    print(f"characters: 8 player frames + 3 npcs + boss (originals backed up to {BACKUP}\\)")
    print("done.")


if __name__ == "__main__":
    main()
