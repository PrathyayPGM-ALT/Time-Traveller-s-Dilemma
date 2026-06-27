"""Character dialogue: a typewriter speech box with optional portrait."""

import math

import pygame

import config
import ui
from textutil import wrap_text, Typewriter, is_shouty


class Line:
    def __init__(self, text, speaker=None, portrait=None, color=None):
        self.text = text
        self.speaker = speaker
        self.portrait = portrait          # a Surface, or None
        self.color = color or config.WHITE


class DialogueBox:
    """Queue-based dialogue. Feed it Lines; advance with Enter/E.

    on_done is called once the whole queue has been dismissed.
    """

    def __init__(self):
        self.queue = []
        self.current = None
        self.typer = None
        self.on_done = None
        self.font = config.font(20)
        self.name_font = config.font(18)

    @property
    def active(self):
        return self.current is not None or bool(self.queue)

    def feed(self, lines, on_done=None):
        # Accept a single string, a Line, or a list of either.
        if isinstance(lines, (str, Line)):
            lines = [lines]
        for ln in lines:
            self.queue.append(ln if isinstance(ln, Line) else Line(ln))
        self.on_done = on_done
        if self.current is None:
            self._next()

    def _next(self):
        if self.queue:
            self.current = self.queue.pop(0)
            self.typer = Typewriter(self.current.text, cps=44)
        else:
            self.current = None
            self.typer = None
            cb, self.on_done = self.on_done, None
            if cb:
                cb()

    def advance(self):
        """Player pressed continue. Reveal fully, or move to next line."""
        if self.current is None:
            return
        if not self.typer.done:
            self.typer.finish()
        else:
            self._next()

    def update(self, dt):
        if self.typer:
            self.typer.update(dt)

    def draw(self, screen):
        if self.current is None:
            return
        W, H = config.WIDTH, config.HEIGHT
        box = pygame.Rect(80, H - 200, W - 160, 150)
        accent = self.current.color
        ui.panel(screen, box, fill=(14, 14, 18, 240), border=(70, 70, 82),
                 accent=accent, radius=10)

        text_x = box.x + 28
        if self.current.portrait is not None:
            frame = pygame.Rect(box.x + 18, box.y + 22, 92, 92)
            pygame.draw.rect(screen, (8, 8, 10), frame, border_radius=6)
            pygame.draw.rect(screen, accent, frame, 2, border_radius=6)
            p = self.current.portrait
            screen.blit(p, (frame.centerx - p.get_width() // 2,
                            frame.centery - p.get_height() // 2))
            text_x = box.x + 130

        top = box.y + 20
        if self.current.speaker:
            ui.text(screen, self.name_font, self.current.speaker, accent, text_x, top)
            top += 30

        visible = self.typer.visible
        shouty = is_shouty(self.current.text)
        for i, line in enumerate(wrap_text(visible, self.font, box.right - text_x - 30)):
            if shouty:
                ui.wavy_text(screen, self.font, line, accent, text_x, top + i * 26)
            else:
                ui.text(screen, self.font, line, config.WHITE, text_x, top + i * 26)

        if self.typer.done:
            a = int(140 + 100 * math.sin(pygame.time.get_ticks() / 250.0))
            ui.text(screen, self.name_font, "> Enter", config.DIM,
                    box.right - 92, box.bottom - 30, alpha=a, shadow=False)
