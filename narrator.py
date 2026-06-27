"""The Narrator: a Stanley-Parable-style voice that comments from on high.

Text-only. Lines may be plain strings or (id, text) tuples — the id is
ignored here (it survives in content.py in case voiced lines return later).
"""

import pygame

import config
import ui
from textutil import wrap_text, Typewriter


class Narrator:
    def __init__(self):
        self.items = []
        self.typer = None
        self.font = config.font(21)
        self.hold = 0.0
        self.fade = 0

    @property
    def active(self):
        return self.typer is not None or bool(self.items)

    @staticmethod
    def _text(item):
        return item[1] if isinstance(item, tuple) else item

    def say(self, lines, interrupt=True):
        if isinstance(lines, (str, tuple)):
            lines = [lines]
        items = [self._text(x) for x in lines]
        if interrupt:
            self.items = items
            self._next()
        else:
            self.items.extend(items)
            if self.typer is None:
                self._next()

    def _next(self):
        if self.items:
            self.typer = Typewriter(self.items.pop(0), cps=40)
            self.hold = 0.0
        else:
            self.typer = None

    def update(self, dt):
        target = 235 if self.active else 0
        self.fade += (target - self.fade) * min(1.0, dt / 180.0)
        if self.typer is None:
            return
        self.typer.update(dt)
        if self.typer.done:
            self.hold += dt / 1000.0
            if self.hold > 1.2 + len(self.typer.text) * 0.018:
                self._next()

    def draw(self, screen):
        if self.fade < 3 or self.typer is None:
            return
        W = config.WIDTH
        alpha = int(self.fade)
        lines = wrap_text(self.typer.visible, self.font, W - 220)
        if lines and any(lines):
            scrim = pygame.Surface((W, 30 * len(lines) + 22), pygame.SRCALPHA)
            for y in range(scrim.get_height()):
                edge = min(y, scrim.get_height() - y)
                scrim.fill((0, 0, 0, min(110, edge * 12)), (0, y, W, 1))
            scrim.set_alpha(alpha)
            screen.blit(scrim, (0, 44))
        for i, line in enumerate(lines):
            ui.text(screen, self.font, line, config.ASH, W // 2, 54 + i * 30,
                    center=True, alpha=alpha, shadow=False)
