"""A code/answer lock — the core puzzle interaction.

You type an answer deduced from clues found around the era. Wrong guesses are
punished (the era raises attention via on_wrong). Result via .done:
None | "success" | "cancel".
"""

import math

import pygame

import config
import ui
from textutil import wrap_text

ACCENT = config.RIFT


class CodeLockModal:
    def __init__(self, prompt, answers, directive="", on_wrong=None):
        self.prompt = prompt
        self.answers = [str(a).lower().strip() for a in answers]
        self.directive = directive
        self.on_wrong = on_wrong
        self.input = ""
        self.done = None
        self.msg = ""
        self.msg_col = config.ASH
        self.shake = 0.0
        self.blink = 0.0
        self.success_pending = 0.0
        self.font = config.font(26)
        self.small = config.font(16)
        self.maxlen = 22

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN or self.success_pending:
            return
        if e.key == pygame.K_ESCAPE:
            self.done = "cancel"
        elif e.key == pygame.K_RETURN:
            self._submit()
        elif e.key == pygame.K_BACKSPACE:
            self.input = self.input[:-1]
        else:
            ch = e.unicode
            if ch and 32 <= ord(ch) < 127 and len(self.input) < self.maxlen:
                self.input += ch

    def _submit(self):
        if self.input.strip().lower() in self.answers:
            self.msg, self.msg_col = "ACCEPTED", config.TITOR
            self.success_pending = 1.0
        else:
            self.msg, self.msg_col = "REJECTED", config.BLOOD
            self.shake = 0.4
            self.input = ""
            if self.on_wrong:
                self.on_wrong()

    def update(self, dt):
        self.blink += dt / 1000.0
        if self.shake > 0:
            self.shake = max(0.0, self.shake - dt / 1000.0)
        if self.success_pending:
            self.success_pending -= dt / 1000.0
            if self.success_pending <= 0:
                self.done = "success"

    def draw(self, screen):
        W, H = config.WIDTH, config.HEIGHT
        ui.scrim(screen, pygame.Rect(0, 0, W, H), 195)
        shake = int(self.shake * 22) if self.shake > 0 else 0
        sx = (pygame.time.get_ticks() % 3 - 1) * shake
        rect = pygame.Rect(W // 2 - 300 + sx, H // 2 - 140, 600, 280)
        ui.panel(screen, rect, fill=(10, 12, 16, 245), border=(*ACCENT, 160),
                 accent=ACCENT, radius=12)

        ui.text(screen, self.small, "LOCK", ACCENT, rect.x + 22, rect.y + 16, shadow=False)
        ui.text(screen, self.small, "Esc: step back", config.DIM,
                rect.right - 22, rect.y + 16, right=True, shadow=False)

        y = rect.y + 44
        for line in wrap_text(self.directive, self.small, rect.w - 60):
            ui.text(screen, self.small, line, config.ASH, rect.centerx, y, center=True)
            y += 22
        ui.text(screen, config.font(20), self.prompt, config.WHITE,
                rect.centerx, y + 6, center=True)

        # input field
        box = pygame.Rect(rect.x + 60, rect.y + 140, rect.w - 120, 48)
        pygame.draw.rect(screen, (6, 8, 10), box, border_radius=6)
        pygame.draw.rect(screen, (*ACCENT, 180), box, 2, border_radius=6)
        cursor = "_" if (self.blink * 2) % 2 < 1 and not self.success_pending else " "
        ui.text(screen, self.font, self.input + cursor, ACCENT,
                box.centerx, box.y + 10, center=True, shadow=False)

        if self.msg:
            ui.text(screen, config.font(18), self.msg, self.msg_col,
                    rect.centerx, rect.bottom - 34, center=True)
