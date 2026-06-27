"""Procedural environment art: themed floors, props, lighting, particles.

Everything is drawn from shapes (we have almost no art), but baked floors +
shaded props + light pools + ambient particles + a colour grade give each
timeline a real sense of place.
"""

import math
import os
import random

import pygame

import config


def _clamp(c, j=0):
    return tuple(max(0, min(255, v + j)) for v in c)


# ---------------------------------------------------------------------------
# Themes: a palette + atmosphere per timeline.
# ---------------------------------------------------------------------------
THEMES = {
    "cafe": {
        "seed": 2001,
        "floor_a": (34, 40, 46), "floor_b": (28, 34, 40), "grout": (20, 24, 28),
        "wall_side": (44, 40, 52), "wall_top": (66, 60, 78), "wall_dark": (24, 22, 30),
        "accent": config.TITOR, "ambient": "dust",
        "grade": (10, 30, 24, 26),
    },
    "garage": {
        "seed": 1998,
        "floor_a": (62, 60, 56), "floor_b": (54, 52, 49), "grout": (40, 39, 36),
        "wall_side": (78, 70, 60), "wall_top": (104, 94, 80), "wall_dark": (44, 40, 34),
        "accent": config.RIFT, "ambient": "dust",
        "grade": (40, 36, 24, 22),
    },
    "observatory": {
        "seed": 1683,
        "floor_a": (40, 42, 50), "floor_b": (33, 35, 43), "grout": (22, 23, 30),
        "wall_side": (52, 52, 60), "wall_top": (74, 74, 86), "wall_dark": (26, 26, 32),
        "accent": config.WARN, "ambient": "embers",
        "grade": (30, 22, 10, 30),
    },
    "ruin": {
        "seed": 3744,
        "floor_a": (30, 29, 31), "floor_b": (24, 23, 25), "grout": (16, 15, 17),
        "wall_side": (46, 40, 42), "wall_top": (64, 56, 58), "wall_dark": (22, 18, 20),
        "accent": config.BLOOD, "ambient": "ash",
        "grade": (20, 8, 8, 34),
    },
    "cave": {
        "seed": 24567,
        "floor_a": (48, 38, 32), "floor_b": (40, 31, 26), "grout": (28, 21, 17),
        "wall_side": (56, 44, 36), "wall_top": (78, 60, 48), "wall_dark": (30, 23, 18),
        "accent": (240, 150, 70), "ambient": "embers",
        "grade": (40, 18, 6, 32),
    },
}


# ---------------------------------------------------------------------------
# Baked floor
# ---------------------------------------------------------------------------
_floor_cache = {}


def bake_floor(theme_key, w, h):
    key = (theme_key, w, h)
    surf = _floor_cache.get(key)
    if surf is not None:
        return surf
    th = THEMES[theme_key]
    rng = random.Random(th["seed"])
    surf = pygame.Surface((w, h))
    tile = 72
    for ty in range(0, h, tile):
        for tx in range(0, w, tile):
            base = th["floor_a"] if (tx // tile + ty // tile) % 2 == 0 else th["floor_b"]
            col = _clamp(base, rng.randint(-7, 7))
            pygame.draw.rect(surf, col, (tx, ty, tile, tile))
            pygame.draw.rect(surf, th["grout"], (tx, ty, tile, tile), 1)
    # speckle / grime
    for _ in range((w * h) // 1100):
        x, y = rng.randint(0, w - 1), rng.randint(0, h - 1)
        surf.set_at((x, y), _clamp(th["floor_a"], rng.randint(-16, 16)))
    # a few darker stains
    for _ in range((w * h) // 90000):
        x, y = rng.randint(40, w - 40), rng.randint(40, h - 40)
        r = rng.randint(20, 60)
        stain = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(stain, (0, 0, 0, 40), (r, r), r)
        surf.blit(stain, (x - r, y - r))
    _floor_cache[key] = surf
    return surf


# ---------------------------------------------------------------------------
# Light pools (additive)
# ---------------------------------------------------------------------------
_light_cache = {}


def _radial(radius, color, max_alpha):
    key = (radius, color, max_alpha)
    s = _light_cache.get(key)
    if s is None:
        s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        steps = 22
        for i in range(steps, 0, -1):
            a = int(max_alpha * (i / steps) ** 2)
            r = int(radius * i / steps)
            pygame.draw.circle(s, (*color, a), (radius, radius), r)
        _light_cache[key] = s
    return s


def draw_light(screen, center, radius, color, max_alpha=110):
    s = _radial(radius, color, max_alpha)
    screen.blit(s, (center[0] - radius, center[1] - radius),
                special_flags=pygame.BLEND_RGBA_ADD)


# ---------------------------------------------------------------------------
# Vignette + colour grade
# ---------------------------------------------------------------------------
_vignette = None


def draw_vignette(screen):
    global _vignette
    if _vignette is None:
        w, h = config.WIDTH, config.HEIGHT
        _vignette = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(120):
            a = int(2.0 * i)
            pygame.draw.rect(_vignette, (0, 0, 0, min(180, a)),
                             (i, i, w - 2 * i, h - 2 * i), 2)
    screen.blit(_vignette, (0, 0))


def draw_grade(screen, theme_key):
    tint = THEMES[theme_key]["grade"]
    overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
    overlay.fill(tint)
    screen.blit(overlay, (0, 0))


# ---------------------------------------------------------------------------
# Ambient particles (screen-space, camera independent)
# ---------------------------------------------------------------------------
class Particles:
    PRESETS = {
        "dust":   dict(n=70, color=(180, 180, 170), vy=(2, 10), vx=(-6, 6), size=(1, 2), a=(20, 60)),
        "ash":    dict(n=90, color=(120, 120, 124), vy=(14, 34), vx=(-10, 6), size=(1, 3), a=(40, 100)),
        "snow":   dict(n=110, color=(220, 224, 232), vy=(18, 40), vx=(-14, 14), size=(1, 3), a=(60, 140)),
        "embers": dict(n=60, color=(240, 150, 70), vy=(-26, -8), vx=(-8, 8), size=(1, 3), a=(40, 130)),
        "void":   dict(n=80, color=(96, 206, 224), vy=(-8, 8), vx=(-8, 8), size=(1, 2), a=(30, 90)),
    }

    def __init__(self, kind):
        self.p = []
        cfg = self.PRESETS.get(kind, self.PRESETS["dust"])
        self.cfg = cfg
        self.rng = random.Random(hash(kind) & 0xffff)
        for _ in range(cfg["n"]):
            self.p.append(self._spawn(initial=True))

    def _spawn(self, initial=False):
        c = self.cfg
        return {
            "x": self.rng.uniform(0, config.WIDTH),
            "y": self.rng.uniform(0, config.HEIGHT) if initial else -4,
            "vx": self.rng.uniform(*c["vx"]),
            "vy": self.rng.uniform(*c["vy"]),
            "s": self.rng.randint(*c["size"]),
            "a": self.rng.randint(*c["a"]),
        }

    def update(self, dt):
        s = dt / 1000.0
        for part in self.p:
            part["x"] += part["vx"] * s
            part["y"] += part["vy"] * s
            if part["y"] > config.HEIGHT + 4 or part["y"] < -8 or \
                    part["x"] < -8 or part["x"] > config.WIDTH + 8:
                part.update(self._spawn())
                if part["vy"] < 0:
                    part["y"] = config.HEIGHT + 4

    def draw(self, screen):
        col = self.cfg["color"]
        for part in self.p:
            surf = pygame.Surface((part["s"] * 2, part["s"] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*col, part["a"]), (part["s"], part["s"]), part["s"])
            screen.blit(surf, (part["x"], part["y"]))


# ---------------------------------------------------------------------------
# Props — each draws within rect r (already in screen space).
# ---------------------------------------------------------------------------
def _block(screen, r, side, top, dark, edge=None):
    pygame.draw.rect(screen, side, r, border_radius=3)
    pygame.draw.rect(screen, top, (r.x, r.y, r.w, max(3, r.h // 4)), border_radius=3)
    pygame.draw.rect(screen, dark, (r.x, r.bottom - 4, r.w, 4))
    pygame.draw.rect(screen, edge or dark, r, 1, border_radius=3)


def p_wall(screen, r, t, th):
    base, top, dark = th["wall_side"], th["wall_top"], th["wall_dark"]
    pygame.draw.rect(screen, base, r)
    pygame.draw.rect(screen, top, (r.x, r.y, r.w, 3))            # lit top edge
    pygame.draw.rect(screen, dark, (r.x, r.bottom - 3, r.w, 3))  # shadowed base
    # offset brick courses
    course = 13
    for i, y in enumerate(range(r.y + course, r.bottom - 2, course)):
        pygame.draw.line(screen, dark, (r.x, y), (r.right, y), 1)
        off = course if i % 2 else 0
        for x in range(r.x - off, r.right, course * 2):
            if r.x < x < r.right:
                pygame.draw.line(screen, dark, (x, y), (x, min(y + course, r.bottom - 3)), 1)
    pygame.draw.rect(screen, dark, r, 1)


def p_counter(screen, r, t, th):
    _block(screen, r, (70, 56, 44), (96, 78, 60), (40, 32, 24))
    pygame.draw.rect(screen, (120, 100, 78), (r.x, r.y, r.w, 6))


def p_table(screen, r, t, th):
    pygame.draw.rect(screen, (40, 34, 30), (r.x + 4, r.bottom - 8, 6, 8))
    pygame.draw.rect(screen, (40, 34, 30), (r.right - 10, r.bottom - 8, 6, 8))
    _block(screen, pygame.Rect(r.x, r.y, r.w, r.h - 6), (96, 78, 58), (120, 100, 76), (54, 44, 32))


def p_chair(screen, r, t, th):
    pygame.draw.rect(screen, (60, 54, 50), r, border_radius=2)
    pygame.draw.rect(screen, (84, 76, 70), (r.x, r.y, r.w, 5))


def p_crt(screen, r, t, th):
    _block(screen, r, (38, 38, 42), (54, 54, 60), (20, 20, 24))
    scr = pygame.Rect(r.x + 6, r.y + 6, r.w - 12, r.h - 16)
    glow = th["accent"]
    pygame.draw.rect(screen, (8, 16, 12), scr)
    pygame.draw.rect(screen, glow, scr, 1)
    # scanlines + cursor
    for i, y in enumerate(range(scr.y + 4, scr.bottom - 3, 6)):
        a = 70 if (i + int(t * 4)) % 4 else 130
        ln = pygame.Surface((scr.w - 6, 2), pygame.SRCALPHA)
        ln.fill((*glow, a))
        screen.blit(ln, (scr.x + 3, y))
    if int(t * 2) % 2 == 0:
        pygame.draw.rect(screen, glow, (scr.x + 4, scr.bottom - 7, 6, 3))


def p_computer(screen, r, t, th):
    _block(screen, r, (206, 198, 178), (224, 218, 200), (150, 142, 124))
    pygame.draw.rect(screen, (60, 70, 64), (r.x + 6, r.y + 6, r.w - 12, r.h // 2))
    pygame.draw.rect(screen, config.RIFT, (r.x + 6, r.y + 6, r.w - 12, r.h // 2), 1)


def p_server(screen, r, t, th):
    _block(screen, r, (30, 30, 34), (44, 44, 50), (16, 16, 18))
    for i, y in enumerate(range(r.y + 6, r.bottom - 6, 10)):
        on = (i + int(t * 3)) % 3 == 0
        pygame.draw.rect(screen, (0, 220, 120) if on else (40, 60, 50),
                         (r.right - 12, y, 5, 5))


def p_shelf(screen, r, t, th):
    _block(screen, r, (74, 60, 46), (96, 80, 62), (40, 32, 24))
    cols = [(150, 60, 60), (60, 110, 150), (150, 140, 70), (90, 140, 90)]
    for i, x in enumerate(range(r.x + 4, r.right - 6, 9)):
        h = 14 + (i * 7) % 18
        pygame.draw.rect(screen, cols[i % len(cols)], (x, r.bottom - h - 4, 6, h))


def p_payphone(screen, r, t, th):
    _block(screen, r, (40, 50, 60), (58, 70, 84), (22, 28, 34))
    pygame.draw.rect(screen, (20, 24, 28), (r.x + 5, r.y + 6, r.w - 10, r.h // 2))
    pygame.draw.rect(screen, (120, 130, 140), (r.x + 7, r.y + 9, 5, r.h // 2 - 6))


def p_plant(screen, r, t, th):
    pygame.draw.rect(screen, (90, 60, 40), (r.centerx - r.w // 4, r.bottom - 10, r.w // 2, 10))
    sway = math.sin(t * 1.5 + r.x) * 2
    pygame.draw.circle(screen, (40, 90, 50), (int(r.centerx + sway), r.y + r.h // 3), r.w // 2)
    pygame.draw.circle(screen, (54, 110, 64), (int(r.centerx + sway), r.y + r.h // 3), r.w // 2, 1)


def p_candle(screen, r, t, th):
    pygame.draw.rect(screen, (210, 200, 180), (r.centerx - 3, r.y + 8, 6, r.h - 8))
    fl = 0.5 + 0.5 * math.sin(t * 9 + r.x)
    h = 8 + fl * 5
    pygame.draw.ellipse(screen, (250, 180, 70),
                        (r.centerx - 3, r.y + 2 - h + 8, 6, h))
    pygame.draw.ellipse(screen, (255, 240, 180),
                        (r.centerx - 1, r.y + 6 - h // 2 + 4, 3, h // 2))


def p_fire(screen, r, t, th):
    for i, log in enumerate([-1, 1]):
        pygame.draw.rect(screen, (70, 50, 36),
                         (r.centerx - 12 + i * 14, r.bottom - 8, 14, 6))
    for k in range(5):
        fl = 0.5 + 0.5 * math.sin(t * 8 + k)
        hx = r.centerx + (k - 2) * 6
        hy = r.bottom - 8 - fl * (18 + k * 2)
        col = (250, 170, 60) if k % 2 else (250, 210, 90)
        pygame.draw.circle(screen, col, (int(hx), int(hy)), int(5 + fl * 3))


def p_pillar(screen, r, t, th):
    _block(screen, r, (74, 74, 82), (96, 96, 106), (40, 40, 46))
    pygame.draw.rect(screen, (96, 96, 106), (r.x - 4, r.y, r.w + 8, 8))
    pygame.draw.rect(screen, (96, 96, 106), (r.x - 4, r.bottom - 8, r.w + 8, 8))


def p_rubble(screen, r, t, th):
    rng = random.Random(r.x * 13 + r.y)
    for _ in range(6):
        x = r.x + rng.randint(0, r.w)
        y = r.y + rng.randint(r.h // 2, r.h)
        s = rng.randint(4, 10)
        pygame.draw.rect(screen, _clamp(th["wall_side"], rng.randint(-10, 10)),
                         (x, y, s, s), border_radius=2)


def p_crate(screen, r, t, th):
    _block(screen, r, (96, 72, 44), (120, 94, 60), (54, 40, 24))
    pygame.draw.line(screen, (54, 40, 24), r.topleft, r.bottomright, 2)
    pygame.draw.line(screen, (54, 40, 24), r.topright, r.bottomleft, 2)


def p_barrel(screen, r, t, th):
    pygame.draw.ellipse(screen, (70, 60, 50), r)
    pygame.draw.ellipse(screen, (96, 84, 70), (r.x, r.y, r.w, r.h // 3))
    pygame.draw.ellipse(screen, (40, 34, 28), r, 2)


def p_telescope(screen, r, t, th):
    pygame.draw.line(screen, (60, 60, 70), (r.x + 4, r.bottom), (r.centerx, r.centery), 4)
    pygame.draw.line(screen, (60, 60, 70), (r.right - 4, r.bottom), (r.centerx, r.centery), 4)
    ang = -0.6 + math.sin(t * 0.4) * 0.1
    dx, dy = math.cos(ang) * r.w * 0.6, math.sin(ang) * r.w * 0.6
    pygame.draw.line(screen, (120, 120, 132),
                     (r.centerx - dx, r.centery - dy), (r.centerx + dx, r.centery + dy), 7)
    pygame.draw.circle(screen, th["accent"], (int(r.centerx + dx), int(r.centery + dy)), 5)


def p_desk(screen, r, t, th):
    _block(screen, r, (70, 58, 44), (94, 78, 60), (40, 32, 24))
    pygame.draw.rect(screen, (54, 44, 32), (r.x + 6, r.y + 8, r.w - 12, 4))


def p_cot(screen, r, t, th):
    _block(screen, r, (60, 54, 60), (80, 72, 80), (34, 30, 36))
    pygame.draw.rect(screen, (170, 170, 180), (r.x + 4, r.y + 4, r.w // 3, r.h - 8), border_radius=3)


def p_tree(screen, r, t, th):
    pygame.draw.rect(screen, (60, 44, 30), (r.centerx - 5, r.bottom - 18, 10, 18))
    sway = math.sin(t + r.x) * 3
    pygame.draw.circle(screen, (34, 70, 44), (int(r.centerx + sway), r.y + r.h // 3), r.w // 2)


def p_stalagmite(screen, r, t, th):
    pygame.draw.polygon(screen, th["wall_side"],
                        [(r.x, r.bottom), (r.right, r.bottom), (r.centerx, r.y)])
    pygame.draw.polygon(screen, th["wall_dark"],
                        [(r.x, r.bottom), (r.right, r.bottom), (r.centerx, r.y)], 1)


def p_painting(screen, r, t, th):
    _block(screen, r, th["wall_side"], th["wall_top"], th["wall_dark"])
    cx, cy = r.center
    pts = []
    for k in range(26):
        ang = k * 0.5 + t * 0.2
        rad = k * (r.w / 60)
        pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.8))
    if len(pts) > 1:
        pygame.draw.lines(screen, (180, 90, 40), False, pts, 2)


def p_monument(screen, r, t, th):
    pygame.draw.polygon(screen, (70, 70, 80),
                        [(r.x, r.bottom), (r.right, r.bottom),
                         (r.right - 6, r.y + 10), (r.centerx, r.y), (r.x + 6, r.y + 10)])
    pygame.draw.polygon(screen, (40, 40, 46),
                        [(r.x, r.bottom), (r.right, r.bottom),
                         (r.right - 6, r.y + 10), (r.centerx, r.y), (r.x + 6, r.y + 10)], 1)
    for y in range(r.y + 20, r.bottom - 8, 8):
        pygame.draw.line(screen, (120, 120, 130), (r.x + 8, y), (r.right - 8, y), 1)


def p_core(screen, r, t, th):
    pulse = 0.5 + 0.5 * math.sin(t * 3)
    pygame.draw.rect(screen, (24, 10, 12), r, border_radius=4)
    inner = r.inflate(-r.w // 3, 0)
    col = (255, int(60 + 120 * pulse), int(60 + 80 * pulse))
    pygame.draw.rect(screen, col, inner, border_radius=4)
    pygame.draw.rect(screen, config.BLOOD, r, 2, border_radius=4)


def p_console(screen, r, t, th):
    _block(screen, r, (34, 40, 46), (52, 60, 68), (18, 22, 26))
    pygame.draw.rect(screen, th["accent"], (r.x + 5, r.y + 5, r.w - 10, r.h // 3), 1)
    for i, x in enumerate(range(r.x + 6, r.right - 8, 10)):
        on = (i + int(t * 4)) % 2 == 0
        pygame.draw.rect(screen, th["accent"] if on else (40, 50, 50),
                         (x, r.bottom - 10, 5, 5))


def p_poster(screen, r, t, th):
    pygame.draw.rect(screen, (200, 196, 180), r)
    pygame.draw.rect(screen, (40, 40, 44), r, 2)
    for y in range(r.y + 8, r.bottom - 6, 8):
        pygame.draw.line(screen, (90, 90, 96), (r.x + 6, y), (r.right - 6, y), 1)


def p_rug(screen, r, t, th):
    s = pygame.Surface(r.size, pygame.SRCALPHA)
    s.fill((90, 40, 40, 90))
    pygame.draw.rect(s, (140, 70, 60, 120), s.get_rect(), 3)
    screen.blit(s, r.topleft)


PROPS = {
    "wall": p_wall, "counter": p_counter, "table": p_table, "chair": p_chair,
    "crt": p_crt, "computer": p_computer, "server": p_server, "shelf": p_shelf,
    "payphone": p_payphone, "plant": p_plant, "candle": p_candle, "fire": p_fire,
    "pillar": p_pillar, "rubble": p_rubble, "crate": p_crate, "barrel": p_barrel,
    "telescope": p_telescope, "desk": p_desk, "cot": p_cot, "tree": p_tree,
    "stalagmite": p_stalagmite, "painting": p_painting, "monument": p_monument,
    "core": p_core, "console": p_console, "poster": p_poster, "rug": p_rug,
}

# Props that emit light: kind -> (color, radius, alpha). Kept subtle so many
# of them don't wash the scene out.
EMITTERS = {
    "crt": (config.TITOR, 64, 30), "computer": (config.RIFT, 60, 26),
    "candle": ((250, 180, 70), 58, 50), "fire": ((250, 170, 70), 150, 80),
    "core": (config.BLOOD, 120, 64), "console": (config.RIFT, 66, 28),
    "server": ((0, 220, 120), 48, 20),
}


# Pixel-art drop-in: if a sprite exists for a prop kind, it replaces the
# procedural drawing. Look first for a theme-specific variant, then a generic
# one:  textures/props/<theme>_<kind>.png   or   textures/props/<kind>.png
_prop_sprite_cache = {}


def _prop_sprite(kind, theme_key):
    key = (kind, theme_key)
    if key in _prop_sprite_cache:
        return _prop_sprite_cache[key]
    surf = None
    for name in (f"{theme_key}_{kind}", kind):
        path = os.path.join("textures", "props", name + ".png")
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
            break
    _prop_sprite_cache[key] = surf
    return surf


def draw_prop(screen, kind, r, t, theme_key):
    sprite = _prop_sprite(kind, theme_key)
    if sprite is not None:
        screen.blit(pygame.transform.scale(sprite, r.size), r.topleft)
        return
    th = THEMES[theme_key]
    fn = PROPS.get(kind, p_wall)
    fn(screen, r, t, th)
