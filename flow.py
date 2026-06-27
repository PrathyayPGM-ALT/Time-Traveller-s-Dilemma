"""Framing scenes: title, opening cutscene, the permanent Troi trap, ending."""

import math

import pygame

import config
import content
import ui
import world
import sound
from scene import Scene
from player import Player
from dialogue import DialogueBox, Line
from narrator import Narrator
from troi import Floater
from cutscene1 import Cutscene1


def _line(d):
    name, path, color = content.SPEAKERS.get(d["who"], (d["who"], None, config.WHITE))
    import assets
    portrait = assets.fit(path, 80, 80) if path else None
    return Line(d["text"], speaker=name, portrait=portrait,
                color=d.get("color", color))


# ---------------------------------------------------------------------------
class TitleScene(Scene):
    def on_enter(self, **kwargs):
        sound.music("title")
        self.t = 0.0
        self.particles = world.Particles("void")
        self.options = []
        f = self.game.flags
        if f.has_run():
            self.options.append(("Continue", self._continue))
        self.options.append(("New journey", self._new))
        self.options.append(("Achievements", self._achievements))
        self.options.append(("Quit", self._quit))
        self.selected = 0

    def _continue(self):
        self.game.go("hub" if self.game.flags["intro_seen"] else "intro")

    def _new(self):
        # The player thinks this is a fresh start. The soul carries over.
        self.game.flags.new_life()
        self.game.go("intro")

    def _achievements(self):
        self.game.go("achievements")

    def _quit(self):
        self.game.running = False

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % len(self.options)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(self.options)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            self.options[self.selected][1]()

    def update(self, dt):
        self.t += dt / 1000.0
        self.particles.update(dt)

    def draw(self, screen):
        screen.fill((7, 8, 12))
        self.particles.draw(screen)

        # rotating spiral behind the title
        cx, cy = config.WIDTH // 2, 215
        pts = []
        for k in range(90):
            ang = k * 0.32 + self.t * 0.3
            rad = k * 1.7
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.42))
        if len(pts) > 1:
            pygame.draw.lines(screen, (24, 60, 70), False, pts, 1)

        glow = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        r = 150 + int(20 * math.sin(self.t * 0.7))
        pygame.draw.ellipse(glow, (*config.RIFT, 18),
                            (cx - r, cy - r // 2, r * 2, r))
        screen.blit(glow, (0, 0))

        ui.text(screen, config.font(54), "TIME TRAVELLER'S", config.WHITE,
                cx, 150, center=True)
        ui.text(screen, config.font(54), "DILEMMA", config.RIFT, cx, 210, center=True)
        ui.text(screen, config.font(18),
                "4200 · the earth is a spoil · the boss is waiting",
                config.DIM, cx, 290, center=True)

        for i, (label, _) in enumerate(self.options):
            sel = i == self.selected
            col = config.WHITE if sel else config.ASH
            ui.text(screen, config.font(26), ("> " if sel else "  ") + label,
                    col, cx, 430 + i * 50, center=True)

        # the meta-hint: faint, deniable, only after a past life
        if self.game.flags["lives"] and self.game.flags["lives"] > 0:
            a = int(40 + 30 * math.sin(self.t * 1.3))
            ui.text(screen, config.font(15), "(you have been here before)",
                    config.DIM, cx, config.HEIGHT - 46, center=True, alpha=a, shadow=False)

        world.draw_vignette(screen)


# ---------------------------------------------------------------------------
class IntroScene(Scene):
    """Wraps the original opening cutscene (kept as-is)."""

    def on_enter(self, **kwargs):
        sound.music("hub")
        self.cutscene = Cutscene1(self.game.screen, config.font(20),
                                  config.WIDTH, config.HEIGHT)
        self._left = False

    def _finish(self):
        if not self._left:
            self._left = True
            self.game.go("hub")     # the boss speaks his intro in the hub

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.cutscene.advance()
            elif event.key == pygame.K_ESCAPE:
                self._finish()

    def update(self, dt):
        self.cutscene.update()
        if self.cutscene.finished():
            self._finish()

    def draw(self, screen):
        self.cutscene.draw()
        a = int(150 + 90 * math.sin(pygame.time.get_ticks() / 400.0))
        ui.text(screen, config.font(16), "Enter: continue      Esc: skip",
                (130, 130, 140), config.WIDTH // 2, config.HEIGHT - 30,
                center=True, alpha=a, shadow=False)


# ---------------------------------------------------------------------------
class TrappedScene(Scene):
    """Caught by the Keepers — trapped in the Troi forever.

    You can walk and talk to the beings (past lives among them), but there is
    no rift. The only way out is to stop playing.
    """

    def on_enter(self, year="?"):
        sound.music("trapped")
        self.game.flags.mark_trapped(year)
        w, h = config.WIDTH, config.HEIGHT
        self.t = 0.0
        self.particles = world.Particles("void")
        self.player = Player(w // 2 - 18, h - 150, speed=3)
        self.player.reset_fade_in()

        voices = content.trapped_voices(self.game.flags)
        n = max(len(voices), content.troi_floaters(self.game.flags))
        self.beings = []
        for i in range(min(n, 18)):
            self.beings.append({"f": Floater(i, w, h), "lines": voices[i % len(voices)]})

        self.dead_rift = pygame.Rect(w // 2 - 55, 150, 110, 110)
        self.dialogue = DialogueBox()
        self.narrator = Narrator()
        self.narrator.say(content.TRAPPED_INTRO)

    def _near(self):
        pc = pygame.Vector2(self.player.center())
        for b in self.beings:
            if pc.distance_to(b["f"].pos + pygame.Vector2(27, 27)) < 70:
                return b
        return None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_q, pygame.K_ESCAPE):
            self.game.running = False
            return
        if self.dialogue.active:
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if event.key == pygame.K_e:
            b = self._near()
            if b:
                self.dialogue.feed([_line(d) for d in b["lines"]])

    def update(self, dt):
        self.t += dt / 1000.0
        self.particles.update(dt)
        self.narrator.update(dt)
        self.dialogue.update(dt)
        for b in self.beings:
            b["f"].update(dt)
        if not self.dialogue.active:
            keys = pygame.key.get_pressed()
            bounds = pygame.Rect(20, 100, config.WIDTH - 40, config.HEIGHT - 120)
            self.player.update(keys, (), bounds)

    def draw(self, screen):
        screen.fill((4, 4, 7))
        self.particles.draw(screen)

        # a dead, closed rift
        pygame.draw.ellipse(screen, (40, 44, 50), self.dead_rift, 2)
        ui.text(screen, config.font(15), "the rift is closed", (60, 64, 70),
                self.dead_rift.centerx, self.dead_rift.bottom + 10, center=True)

        near = None if self.dialogue.active else self._near()
        for b in self.beings:
            b["f"].draw(screen)
            if b is near:
                p = b["f"].pos
                ui.text(screen, config.font(15), "[ E ] speak", config.ASH,
                        p.x + 27, p.y - 16, center=True)

        self.player.draw(screen)

        ui.text(screen, config.font(26), "CAUGHT IN THE TROI", config.BLOOD,
                config.WIDTH // 2, 14, center=True)
        self.narrator.draw(screen)

        # the only exit
        a = int(120 + 90 * math.sin(self.t * 2))
        ui.text(screen, config.font(17), "There is no way out.  Press Q or Esc to give up.",
                config.ASH, config.WIDTH // 2, config.HEIGHT - 40, center=True, alpha=a)

        world.draw_vignette(screen)
        self.dialogue.draw(screen)


# ---------------------------------------------------------------------------
class EndingScene(Scene):
    """The loop closes. You were always the boss."""

    LINES = [
        "You step into the machine.",
        "The Troi takes you, the way it always does.",
        "You drift, and you forget, the way you always do.",
        "Somewhere, a younger you wakes in a borrowed body",
        "and hears a dark, familiar voice call them Prisoner 7.",
        "",
        "You were the boss. You were always the boss.",
        "The war you were sent to stop is the war you keep scheduling.",
        "",
        "And the spiral on the cave wall gains one more mark.",
    ]

    def on_enter(self, **kwargs):
        sound.music("ending")
        self.t = 0.0
        self.game.flags.mark_ending()

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.t > 3 and \
                event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.game.go("title")

    def update(self, dt):
        self.t += dt / 1000.0

    def draw(self, screen):
        screen.fill((6, 7, 10))
        cx, cy = config.WIDTH // 2, 200
        pts = []
        for k in range(120):
            ang = k * 0.3 + self.t * 0.4
            rad = k * 1.2
            pts.append((cx + math.cos(ang) * rad, cy + math.sin(ang) * rad * 0.5))
        if len(pts) > 1:
            pygame.draw.lines(screen, (30, 70, 80), False, pts, 1)

        reveal = self.t / 1.4
        for i, line in enumerate(self.LINES):
            if i > reveal:
                break
            a = min(255, int((reveal - i) * 255))
            col = config.RIFT if "boss" in line else config.ASH
            ui.text(screen, config.font(22), line, col, cx, 340 + i * 34,
                    center=True, alpha=a)

        if self.t > 3:
            a = int(120 + 100 * math.sin(self.t * 3))
            ui.text(screen, config.font(18), "Press Enter", config.DIM,
                    cx, config.HEIGHT - 50, center=True, alpha=a)
        world.draw_vignette(screen)


# ---------------------------------------------------------------------------
class AchievementsScene(Scene):
    """The soul's ledger — what this player has done across all lives."""

    def on_enter(self, **kwargs):
        self.t = 0.0
        self.particles = world.Particles("void")

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE,
                pygame.K_e, pygame.K_q, pygame.K_BACKSPACE):
            self.game.go("title")

    def update(self, dt):
        self.t += dt / 1000.0
        self.particles.update(dt)

    def draw(self, screen):
        screen.fill((7, 8, 12))
        self.particles.draw(screen)
        cx = config.WIDTH // 2

        unlocked = self.game.flags["achievements"] or []
        total = len(content.ACHIEVEMENTS)

        ui.text(screen, config.font(40), "ACHIEVEMENTS", config.WHITE, cx, 50,
                center=True)
        ui.text(screen, config.font(16),
                "%d / %d unlocked" % (len(unlocked), total),
                config.DIM, cx, 100, center=True, shadow=False)

        x = cx - 300
        y = 160
        for a in content.ACHIEVEMENTS:
            got = a["id"] in unlocked
            if got:
                ui.text(screen, config.font(23), "[x]  %s" % a["name"],
                        config.TITOR, x, y)
                ui.text(screen, config.font(15), a["desc"], config.DIM,
                        x + 44, y + 30, shadow=False)
            else:
                # locked: keep it a mystery until earned
                ui.text(screen, config.font(23), "[ ]  ? ? ?",
                        (70, 72, 80), x, y)
                ui.text(screen, config.font(15), "locked", (58, 60, 68),
                        x + 44, y + 30, shadow=False)
            y += 74

        a = int(120 + 90 * math.sin(self.t * 2))
        ui.text(screen, config.font(16), "Esc — back", config.DIM, cx,
                config.HEIGHT - 44, center=True, alpha=a, shadow=False)
        world.draw_vignette(screen)
