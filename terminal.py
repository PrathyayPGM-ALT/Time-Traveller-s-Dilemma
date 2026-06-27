"""A fake shell you actually type into — used for diegetic tasks.

Config (a dict):
    host:     "timetravel_0@troi"        prompt host
    goal:     "Read warning.txt, post it."   shown at top
    intro:    [str, ...]                 banner lines
    files:    {"name": [line, ...]}      readable with `cat`
    win_cmds: ["post warning.txt", ...]  commands that complete the task
    win:      [str, ...]                 output printed on success

Generic commands: help, ls, cat <file>, whoami, clear, plus the win commands.
Result is exposed via .done -> None | "success" | "cancel".
"""

import pygame

import config
import ui

GREEN = config.TITOR
DIMG = (70, 120, 86)
GOALC = (214, 196, 120)


class TerminalModal:
    def __init__(self, cfg):
        self.host = cfg.get("host", "user@troi")
        self.user = self.host.split("@")[0]
        self.files = {k.lower(): v for k, v in cfg.get("files", {}).items()}
        self.win_cmds = [c.lower() for c in cfg.get("win_cmds", [])]
        self.win_out = cfg.get("win", ["done."])
        self.goal = cfg.get("goal", "")
        self.lines = list(cfg.get("intro", []))
        self.input = ""
        self.done = None
        self.blink = 0.0
        self.success_pending = 0.0
        self.font = config.font(18)
        self.maxlen = 52

    def _prompt(self):
        return f"{self.host}:~$ "

    def handle_event(self, e):
        if e.type != pygame.KEYDOWN or self.success_pending:
            return
        if e.key == pygame.K_ESCAPE:
            self.done = "cancel"
        elif e.key == pygame.K_RETURN:
            self._run(self.input.strip())
            self.input = ""
        elif e.key == pygame.K_BACKSPACE:
            self.input = self.input[:-1]
        else:
            ch = e.unicode
            if ch and 32 <= ord(ch) < 127 and len(self.input) < self.maxlen:
                self.input += ch

    def _echo(self, s=""):
        self.lines.append(s)

    def _run(self, raw):
        self._echo(self._prompt() + raw)
        cmd = raw.lower()
        if cmd in self.win_cmds:
            for ln in self.win_out:
                self._echo(ln)
            self.success_pending = 1.4
            return
        parts = cmd.split()
        if not parts:
            return
        c = parts[0]
        if c == "help":
            verbs = "help, ls, cat <file>, whoami, clear"
            if self.win_cmds:
                verbs += ", " + self.win_cmds[0].split()[0] + " <file>"
            self._echo("commands: " + verbs)
        elif c == "ls":
            self._echo("  ".join(self.files.keys()) or "(empty)")
        elif c == "whoami":
            self._echo(self.user)
        elif c == "clear":
            self.lines = []
        elif c == "cat":
            if len(parts) < 2:
                self._echo("usage: cat <file>")
            elif parts[1] in self.files:
                for ln in self.files[parts[1]]:
                    self._echo(ln)
            else:
                self._echo(f"cat: {parts[1]}: no such file")
        else:
            self._echo(f"command not found: {c}   (try 'help')")

    def update(self, dt):
        self.blink += dt / 1000.0
        if self.success_pending:
            self.success_pending -= dt / 1000.0
            if self.success_pending <= 0:
                self.done = "success"

    def draw(self, screen):
        W, H = config.WIDTH, config.HEIGHT
        ui.scrim(screen, pygame.Rect(0, 0, W, H), 190)
        rect = pygame.Rect(60, 64, W - 120, H - 150)
        pygame.draw.rect(screen, (6, 10, 8), rect, border_radius=8)
        pygame.draw.rect(screen, (40, 90, 60), rect, 2, border_radius=8)

        bar = pygame.Rect(rect.x, rect.y, rect.w, 30)
        pygame.draw.rect(screen, (16, 28, 20), bar,
                         border_top_left_radius=8, border_top_right_radius=8)
        ui.text(screen, config.font(16), f"{self.user} — secure shell",
                GREEN, rect.x + 12, rect.y + 6, shadow=False)
        ui.text(screen, config.font(15), "Esc: step away", DIMG,
                rect.right - 12, rect.y + 7, right=True, shadow=False)

        y = rect.y + 40
        if self.goal:
            ui.text(screen, config.font(15), "GOAL: " + self.goal, GOALC,
                    rect.x + 14, y, shadow=False)
            y += 26

        line_h = 22
        avail = max(0, (rect.bottom - 18 - y) // line_h - 1)
        for ln in self.lines[-avail:]:
            ui.text(screen, self.font, ln, GREEN, rect.x + 14, y, shadow=False)
            y += line_h

        cursor = "_" if (self.blink * 2) % 2 < 1 else " "
        shown = self._prompt() if self.success_pending else self._prompt() + self.input + cursor
        ui.text(screen, self.font, shown, GREEN, rect.x + 14, y, shadow=False)
