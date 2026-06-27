"""Orientation: the boss walks you through the controls before missions.

He is not happy about it. Teaches: move (WASD), interact (E), use a terminal,
and explains attention / Time Keepers / rifts. Runs once automatically (soul
flag 'trained'), replayable from the hub.
"""

import math

import pygame

import config
import assets
import content
import world
import ui
import sound
from scene import Scene
from player import Player
from dialogue import DialogueBox, Line
from terminal import TerminalModal


def _line(d):
    name, path, color = content.SPEAKERS.get(d["who"], (d["who"], None, config.WHITE))
    portrait = assets.fit(path, 80, 80) if path else None
    return Line(d["text"], speaker=name, portrait=portrait, color=color)


say = content.say

INTRO = [
    say("boss", "Orientation. Again. New body, same lump of instincts."),
    say("boss", "I'll go slowly. Historically, you have needed slowly."),
    say("boss", "Three things: move, interact, and — stay with me — actually do the work."),
]
MOVE_DONE = [say("boss", "You walked onto a glowing square. A triumph. "
                         "Future generations will weep with pride.")]
INTERACT_DONE = [
    say("boss", "You pressed E. The 'E' is for 'effort'. I am being generous."),
    say("boss", "Some things need more than a button. That TERMINAL takes typed "
                "commands. Open it, read what it asks, and type exactly that."),
    say("boss", "It will tell you the commands. When in doubt: type  help."),
]
TERMINAL_DONE = [
    say("boss", "You typed words and the machine obeyed. Don't let it go to your head."),
    say("boss", "Out there, every year is watching. Wander off the task and your "
                "'attention' climbs — top-right of your eye."),
    say("boss", "Fill it and the Time Keepers come. They do not bargain. They keep."),
    say("boss", "If they take you, you stay in the Troi. Forever. I'll be sad for "
                "almost a whole second."),
    say("boss", "Finish the work and a rift opens. It glows when you've earned it. "
                "Use it. Now go stand in this one and stop wasting my millennia."),
]

PRACTICE = {
    "host": "recruit@troi",
    "goal": "Type a command, press Enter.  Try:  ls  →  cat drill.txt  →  post drill.txt",
    "intro": ["orientation shell — type a command and press Enter.",
              "type  help  to list commands.  type  ls  to see files."],
    "files": {"drill.txt": ["This is a practice payload.",
                            "To finish: type  post drill.txt  and press Enter."]},
    "win_cmds": ["post drill.txt", "post drill"],
    "win": ["posting...", "fine. you can press buttons. don't gloat.",
            "orientation almost over."],
}

TASKS = {
    "move": "Walk onto the glowing MARKER.   (WASD / Arrow keys)",
    "interact": "Press E at the CONSOLE.",
    "terminal": "Press E at the TERMINAL, then type:  post drill.txt   (Enter)",
    "exit": "Step into the RIFT to finish.",
}


class TrainingScene(Scene):
    def on_enter(self, **kwargs):
        self.t = 0.0
        self.particles = world.Particles("void")
        self.player = Player(480, 600, speed=4)
        self.player.reset_fade_in()

        self.pad = pygame.Rect(450, 380, 100, 100)
        self.console = pygame.Rect(180, 470, 80, 70)
        self.term = pygame.Rect(740, 470, 80, 80)
        self.rift = pygame.Rect(455, 200, 90, 90)

        self.dialogue = DialogueBox()
        self.modal = None
        self.phase = "talk"
        self.dialogue.feed([_line(d) for d in INTRO], on_done=lambda: self._set("move"))

    @property
    def capturing_text(self):
        return self.modal is not None

    def _set(self, phase):
        self.phase = phase

    def _near(self, rect):
        return self.player.rect().colliderect(rect.inflate(70, 70))

    def handle_event(self, event):
        if self.modal:
            self.modal.handle_event(event)
            return
        if event.type != pygame.KEYDOWN:
            return
        if self.dialogue.active:
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if event.key == pygame.K_e:
            if self.phase == "interact" and self._near(self.console):
                self._set("talk")
                self.dialogue.feed([_line(d) for d in INTERACT_DONE],
                                   on_done=lambda: self._set("terminal"))
            elif self.phase == "terminal" and self._near(self.term):
                self.modal = TerminalModal(PRACTICE)

    def update(self, dt):
        self.t += dt / 1000.0
        self.particles.update(dt)
        self.dialogue.update(dt)

        if self.modal:
            self.modal.update(dt)
            if self.modal.done:
                ok = self.modal.done == "success"
                self.modal = None
                if ok:
                    self._set("talk")
                    self.dialogue.feed([_line(d) for d in TERMINAL_DONE],
                                       on_done=lambda: self._set("exit"))
            sound.footsteps(False)
            return

        if self.dialogue.active:
            sound.footsteps(False)
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, [self.console, self.term],
                           pygame.Rect(40, 110, config.WIDTH - 80, config.HEIGHT - 130))
        sound.footsteps(self.player.moved_this_frame)

        if self.phase == "move" and self._near(self.pad):
            self._set("talk")
            self.dialogue.feed([_line(d) for d in MOVE_DONE],
                               on_done=lambda: self._set("interact"))
        elif self.phase == "exit" and self.player.rect().colliderect(self.rift):
            self.game.flags["trained"] = True
            self.game.flags.save()
            self.game.go("hub")

    def draw(self, screen):
        screen.fill((10, 10, 14))
        self.particles.draw(screen)

        ui.text(screen, config.font(22), "ORIENTATION", config.BLOOD, 24, 16)
        ui.text(screen, config.font(15), "the boss is running this. reluctantly.",
                config.DIM, 24, 46, shadow=False)

        active = self.phase
        self._marker(screen, self.pad, "MARKER", active == "move", glow=True)
        world.draw_prop(screen, "console", self.console, self.t, "ruin")
        self._tag(screen, self.console, "CONSOLE", active == "interact")
        world.draw_prop(screen, "crt", self.term, self.t, "cafe")
        self._tag(screen, self.term, "TERMINAL", active == "terminal")
        self._rift(screen, active == "exit")

        self.player.draw(screen)

        task = TASKS.get(self.phase)
        if task and not self.dialogue.active:
            f = config.font(17)
            tw = f.size(task)[0]
            pw = tw + 44
            p = pygame.Rect(config.WIDTH // 2 - pw // 2, config.HEIGHT - 96, pw, 42)
            ui.panel(screen, p, accent=config.RIFT)
            ui.text(screen, f, task, config.WHITE,
                    config.WIDTH // 2, p.y + 11, center=True)

        world.draw_vignette(screen)
        self.dialogue.draw(screen)
        if self.modal:
            self.modal.draw(screen)

    def _marker(self, screen, rect, label, active, glow=False):
        pulse = 0.5 + 0.5 * math.sin(self.t * 3)
        col = config.RIFT if active else (70, 90, 96)
        if active and glow:
            world.draw_light(screen, rect.center, 80, config.RIFT, 60)
        pygame.draw.ellipse(screen, col, rect, 2)
        if active:
            ui.text(screen, config.font(15), label, col,
                    rect.centerx, rect.bottom + 6, center=True)

    def _tag(self, screen, rect, label, active):
        if not active:
            return
        bob = math.sin(self.t * 3 + rect.x) * 3
        world.draw_light(screen, rect.center, 60, config.RIFT, 45)
        ui.text(screen, config.font(16), label, config.WHITE,
                rect.centerx, rect.top - 28, center=True)
        if self._near(rect):
            ui.text(screen, config.font(15), "[ E ]", config.RIFT,
                    rect.centerx, rect.bottom + 6, center=True)

    def _rift(self, screen, ready):
        ring = config.RIFT if ready else (60, 72, 78)
        pulse = 0.5 + 0.5 * math.sin(self.t * 2.6)
        if ready:
            for i in range(5):
                rr = self.rift.inflate(i * 16, i * 16)
                surf = pygame.Surface((rr.width, rr.height), pygame.SRCALPHA)
                pygame.draw.ellipse(surf, (*ring, int(90 * pulse / (i + 1))), surf.get_rect())
                screen.blit(surf, rr.topleft)
        pygame.draw.ellipse(screen, ring, self.rift, 2)
        if ready:
            ui.text(screen, config.font(15), "the rift", ring,
                    self.rift.centerx, self.rift.bottom + 8, center=True)
