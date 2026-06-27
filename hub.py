"""The 4200 hub: the boss's domain and the time-machine console.

The boss looms here. A terminal lists the years you can jump to. Selecting a
year plays the boss's briefing, then sends you through the Troi.
"""

import math
import random

import pygame

import config
import assets
import content
import ui
import sound
from scene import Scene
from dialogue import DialogueBox, Line
from narrator import Narrator


class HubScene(Scene):
    def on_enter(self, **kwargs):
        sound.music("hub")
        self.t = 0.0
        self.boss = assets.image("textures/boss.png", (220, 440))
        self.subtitle = random.choice(content.HUB_SUBTITLES)
        self.dialogue = DialogueBox()
        self.narrator = Narrator()
        self.selected = 0
        self.menu_locked = True   # unlocked once any opening dialogue closes

        # an achievement unlocked while jumping (e.g. escaping the Keepers)
        self.new_achievements = self.game.pending_toasts[:]
        self.game.pending_toasts.clear()
        self.achv_t = 0.0 if self.new_achievements else 99.0
        self.entries = ([("training", "orientation")]
                        + [(k, content.ERAS[k]["title"]) for k in content.ERA_ORDER])

        flags = self.game.flags
        all_done = all(flags.done(k) for k in content.ERA_ORDER)

        if not flags["intro_seen"]:
            self.dialogue.feed([self._line(d) for d in content.boss_intro(flags)],
                               on_done=self._after_intro)
        elif all_done and not flags["run_ended"]:
            self.dialogue.feed([self._line(d) for d in content.BOSS_ALL_DONE],
                               on_done=lambda: self.game.go("ending"))
        else:
            self.dialogue.feed([self._line(d) for d in content.boss_return(flags)],
                               on_done=self._unlock)

    # -- helpers ---------------------------------------------------------
    def _line(self, d):
        name, path, color = content.SPEAKERS.get(
            d["who"], (d["who"], None, config.WHITE))
        portrait = assets.fit(path, 80, 80) if path else None
        return Line(d["text"], speaker=name, portrait=portrait, color=color)

    def _unlock(self):
        self.menu_locked = False

    def _after_intro(self):
        self.game.flags["intro_seen"] = True
        self.game.flags.save()
        if not self.game.flags["trained"]:
            self.game.go("training")     # the boss insists on orientation
        else:
            self.menu_locked = False

    def _select(self, entry_id):
        if entry_id == "training":
            self.game.go("training")
            self.menu_locked = True
        else:
            brief = content.ERAS[entry_id]["brief"]
            self.dialogue.feed([self._line(d) for d in brief],
                               on_done=lambda: self.game.go("troi", destination=entry_id))
            self.menu_locked = True

    # -- loop ------------------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.dialogue.active:
            if event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
                self.dialogue.advance()
            return
        if self.menu_locked:
            return
        if event.key in (pygame.K_w, pygame.K_UP):
            self.selected = (self.selected - 1) % len(self.entries)
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.selected = (self.selected + 1) % len(self.entries)
        elif event.key in (pygame.K_RETURN, pygame.K_e, pygame.K_SPACE):
            self._select(self.entries[self.selected][0])

    def update(self, dt):
        self.t += dt / 1000.0
        self.achv_t += dt / 1000.0
        self.dialogue.update(dt)
        self.narrator.update(dt)

    # -- draw ------------------------------------------------------------
    def draw(self, screen):
        # bleak red-black gradient
        screen.fill((14, 8, 9))
        glow = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
        r = 120 + int(20 * math.sin(self.t))
        pygame.draw.ellipse(glow, (40, 6, 8, 90),
                            (config.WIDTH // 2 - r, -80, r * 2, 360))
        screen.blit(glow, (0, 0))

        # the boss, looming and faintly breathing
        bob = math.sin(self.t * 0.8) * 6
        sway = math.sin(self.t * 1.1) * 4
        boss = self.boss.copy()
        boss.set_alpha(220)
        screen.blit(boss, (config.WIDTH // 2 - boss.get_width() // 2 + sway, 24 + bob))

        ui.text(screen, config.font(26), "4200", config.BLOOD, 24, 16)
        ui.text(screen, config.font(17), self.subtitle, config.DIM, 24, 52)

        lives = self.game.flags["lives"]
        if lives and lives > 1:
            ui.text(screen, config.font(16),
                    "incarnation %d" % lives, (90, 40, 44),
                    config.WIDTH - 24, 18, right=True)

        if not self.dialogue.active and not self.menu_locked:
            self._draw_menu(screen)

        ui.achievement_toast(screen, self.new_achievements, self.achv_t)
        self.narrator.draw(screen)
        self.dialogue.draw(screen)

    def _draw_menu(self, screen):
        x, y0 = config.WIDTH // 2 - 240, 470
        ui.text(screen, config.font(20), "TIME MACHINE — choose a destination",
                config.RIFT, config.WIDTH // 2, y0 - 42, center=True)

        for i, (eid, title) in enumerate(self.entries):
            sel = i == self.selected
            row = pygame.Rect(x, y0 + i * 46, 480, 40)
            if sel:
                ui.panel(screen, row, fill=(*config.RIFT, 32),
                         border=(*config.RIFT, 150), accent=config.RIFT, radius=8)

            if eid == "training":
                done = self.game.flags["trained"]
                label = "TRAINING"
            else:
                done = self.game.flags.done(eid)
                label = eid
            mark = "[x]" if done else "[ ]"
            col = config.TITOR if done else (config.WHITE if sel else config.ASH)
            ui.text(screen, config.font(21), f"{mark} {label}", col, row.x + 16, row.y + 8)
            ui.text(screen, config.font(15), title, config.DIM,
                    row.x + 200, row.y + 12, shadow=False)

        ui.text(screen, config.font(16), "W/S to choose · Enter to select",
                config.DIM, config.WIDTH // 2,
                y0 + len(self.entries) * 46 + 10, center=True)
