"""A data-driven, explorable era world.

Each era is a top-down place you walk across, divided into named zones you
"travel" between. It has scenery (decor props), walls, wandering NPCs,
collectible items, and a multi-step quest. Diverging draws the Time Keepers.
"""

import math
import random

import pygame

import config
import assets
import content
import world
import worldgen
import ui
import sound
from scene import Scene
from codelock import CodeLockModal
from player import Player, SIZE as PSIZE
from dialogue import DialogueBox, Line
from narrator import Narrator
from timekeeper import TimeKeeper
from textutil import wrap_text


class Interactable:
    """A static thing you can press E on (terminal, notice, rift, ...)."""

    def __init__(self, d):
        self.id = d["id"]
        self.rect = pygame.Rect(d["x"], d["y"], d["w"], d["h"])
        self.label = d["label"]
        self.kind = d.get("kind", "task")
        self.prop = d.get("prop", "console")
        self.lines = d.get("lines", [])
        self.risky = d.get("risky", False)
        self.gives = d.get("gives")
        self.solid = d.get("solid", True)
        self.terminal = d.get("terminal")
        self.take = d.get("take")
        self.used = False

    @property
    def base_y(self):
        return self.rect.bottom

    @property
    def hot(self):
        return self.rect.inflate(70, 70)

    def draw(self, screen, cam, t, theme):
        r = self.rect.move(-cam[0], -cam[1])
        if self.kind == "exit":
            return
        world.draw_prop(screen, self.prop, r, t, theme)


class WanderNPC:
    """A person who drifts around their spot and can be talked to."""

    def __init__(self, d):
        self.id = d["id"]
        self.label = d["label"]
        self.kind = "npc"
        self.lines = d.get("lines", [])
        self.risky = d.get("risky", False)
        self.gives = d.get("gives")
        self.take = None
        self.used = False
        self.sprite_idx = d.get("sprite", 1)
        sz = 44
        self.image = assets.image(f"textures/npc{self.sprite_idx}.png", (sz, sz))
        self.size = sz
        self.home = pygame.Vector2(d["x"], d["y"])
        self.pos = pygame.Vector2(d["x"], d["y"])
        self.radius = d.get("radius", 70)
        self.target = pygame.Vector2(self.pos)
        self.wait = random.uniform(0, 2)
        self.phase = random.random() * 6.28
        self.rng = random.Random(self.id.__hash__() & 0xffff)

    @property
    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)

    @property
    def base_y(self):
        return self.pos.y + self.size

    @property
    def hot(self):
        return self.rect.inflate(76, 76)

    def update(self, dt):
        self.phase += dt / 400.0
        if self.wait > 0:
            self.wait -= dt / 1000.0
            return
        d = self.target - self.pos
        if d.length() < 4:
            self.target = self.home + pygame.Vector2(
                self.rng.uniform(-self.radius, self.radius),
                self.rng.uniform(-self.radius, self.radius))
            self.wait = self.rng.uniform(0.6, 2.6)
        else:
            self.pos += d.normalize() * 1.1

    def draw(self, screen, cam, t, theme):
        bob = math.sin(self.phase) * 2
        sx, sy = self.pos.x - cam[0], self.pos.y - cam[1]
        shadow = pygame.Surface((self.size - 12, self.size // 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        screen.blit(shadow, (sx + 6, sy + self.size - self.size // 7))
        screen.blit(self.image, (sx, sy + bob))


class EraScene(Scene):
    SUSPICION_MAX = 100

    def on_enter(self, key="2001"):
        self.key = key
        self.data = content.ERAS[key]
        self.theme = self.data["theme"]
        self.accent = world.THEMES[self.theme]["accent"]
        sound.music("era_" + self.theme)

        base = self.game.flags["run_seed"] or 1
        seed = (base * 100003 + sum(ord(c) for c in key)) & 0x7fffffff
        layout = worldgen.build(self.data, seed)

        self.world = pygame.Rect(0, 0, *layout["world"])
        self.floor = world.bake_floor(self.theme, self.world.width, self.world.height)
        self.particles = world.Particles(world.THEMES[self.theme]["ambient"])

        sx, sy = layout["spawn"]
        self.player = Player(sx, sy, speed=4)
        self.player.reset_fade_in()

        self.walls = [pygame.Rect(*w) for w in layout["walls"]]
        self.decor = [dict(d, rect=pygame.Rect(d["x"], d["y"], d["w"], d["h"]))
                      for d in layout["decor"]]
        self.zones = layout["zones"]

        self.objects = [Interactable(o) for o in layout["objects"]]
        self.npcs = [WanderNPC(n) for n in layout["npcs"]]

        self.puzzle = self.data["puzzle"]
        self.lock_id = self.puzzle["lock"]
        self.solved = self.game.flags.done(key)

        self.dialogue = DialogueBox()
        self.narrator = Narrator()
        self.narrator.say(self.data["arrival"])

        instab = self.game.flags["instability"]
        self.suspicion = min(40.0, instab * 8.0)
        self.warned = False
        self.keepers = []
        self.caught = False
        self.grace = max(3.0, 10.0 - instab)
        self.flash = 0.0
        self.t = 0.0
        self.cur_zone = None
        self.zone_title = ""
        self.zone_t = 0.0

        self.modal = None
        self.rift = next((o for o in self.objects if o.kind == "exit"), None)

        self.new_achievements = []
        self.achv_t = 99.0

    @property
    def capturing_text(self):
        return self.modal is not None

    @property
    def quest_done(self):
        return self.solved

    def _line(self, d):
        name, path, color = content.SPEAKERS.get(
            d["who"], (d["who"], None, config.WHITE))
        portrait = assets.fit(path, 80, 80) if path else None
        return Line(d["text"], speaker=name, portrait=portrait,
                    color=d.get("color", color))

    @staticmethod
    def _collide(rect):
        return rect.inflate(-min(rect.w - 8, rect.w // 5),
                            -min(rect.h - 8, rect.h // 5))

    def _solids(self):
        s = list(self.walls)
        s += [self._collide(d["rect"]) for d in self.decor if d.get("solid", True)]
        s += [self._collide(o.rect) for o in self.objects
              if o.kind != "exit" and o.solid]
        return s

    def _interactables(self):
        return self.objects + self.npcs

    def _is_lock(self, obj):
        return obj.id == self.lock_id and not self.solved

    def _near(self):
        pr = self.player.rect()
        best, bestd = None, 1e9
        for obj in self._interactables():
            pending_take = obj.take and not self._taken(obj)
            if obj.kind != "exit" and obj.used and not pending_take \
                    and not self._is_lock(obj):
                continue
            if pr.colliderect(obj.hot):
                d = pygame.Vector2(obj.rect.center).distance_to(self.player.center())
                if d < bestd:
                    best, bestd = obj, d
        return best

    def _taken(self, obj):
        return obj.take and obj.take in self.game.flags["satchel"]

    def _near_takeable(self):
        pr = self.player.rect()
        for obj in self.objects:
            if obj.take and not self._taken(obj) and pr.colliderect(obj.hot):
                return obj
        return None

    def _take(self, obj):
        item = obj.take
        flags = self.game.flags
        if not item or item in flags["satchel"]:
            return
        flags["satchel"].append(item)
        flags["instability"] = flags["instability"] + 1
        flags["defiance"] = flags["defiance"] + 1
        flags.save()
        sound.sfx("take")
        self.flash = 1.0
        self.narrator.say([
            f"You take {item}. It shouldn't leave this year.",
            "A rift tears behind you. The Keepers feel everything you carry.",
        ])
        self._raise_suspicion(60)

    def _camera(self):
        cx = self.player.pos.x + PSIZE // 2 - config.WIDTH // 2
        cy = self.player.pos.y + PSIZE // 2 - config.HEIGHT // 2
        cx = max(0, min(cx, self.world.width - config.WIDTH))
        cy = max(0, min(cy, self.world.height - config.HEIGHT))
        return int(cx), int(cy)

    def _raise_suspicion(self, amount):
        if self.quest_done:
            return
        self.suspicion = min(self.SUSPICION_MAX, self.suspicion + amount)
        if self.suspicion >= 60 and not self.warned:
            self.warned = True
            self.narrator.say(content.NARR_KEEPER_WATCH)
        if self.suspicion >= self.SUSPICION_MAX and not self.keepers:
            self._spawn_keepers()

    def _spawn_keepers(self):
        sound.sfx("keeper")
        self.narrator.say(content.NARR_KEEPER_SPAWN)
        instab = self.game.flags["instability"]
        count = 2 + min(instab, 4)
        speed = 2.5 + 0.25 * min(instab, 4)
        for _ in range(count):
            edge = random.choice(["top", "bottom", "left", "right"])
            if edge == "top":
                p = (random.randint(0, self.world.width), -40)
            elif edge == "bottom":
                p = (random.randint(0, self.world.width), self.world.height + 40)
            elif edge == "left":
                p = (-40, random.randint(0, self.world.height))
            else:
                p = (self.world.width + 40, random.randint(0, self.world.height))
            self.keepers.append(TimeKeeper(*p, speed=speed))

    def _interact(self, obj):
        if obj.kind == "exit":
            self._use_rift()
            return
        if obj.id == self.lock_id:
            if self.solved:
                return
            sound.sfx("interact")
            self.modal = CodeLockModal(self.puzzle["prompt"], self.puzzle["answer"],
                                       directive=self.puzzle["directive"],
                                       on_wrong=self._wrong_code)
            return
        if obj.used:
            return
        sound.sfx("interact")
        obj.used = True
        self.dialogue.feed([self._line(d) for d in obj.lines],
                           on_done=lambda o=obj: self._after_lore(o))

    def _solve(self):
        self.solved = True
        lock = next((o for o in self._interactables() if o.id == self.lock_id), None)
        if lock:
            lock.used = True
        self.game.flags.complete(self.key)
        if self.key == "24567 BC":
            self.game.flags["titor_truth"] = True
        self.game.flags.save()
        self.new_achievements = self.game.flags.sync_achievements()
        if self.new_achievements:
            self.achv_t = 0.0
        sound.sfx("rift")
        self.dialogue.feed([self._line(d) for d in self.puzzle.get("solved", [])])
        self.narrator.say(content.NARR_WORK_DONE)

    def _wrong_code(self):
        sound.sfx("keeper")
        self.flash = 0.6
        self._raise_suspicion(34)

    def _after_lore(self, obj):
        if obj.risky:
            self.game.flags["defiance"] = self.game.flags["defiance"] + 1
            self._raise_suspicion(36)
            self.narrator.say(random.choice(content.NARR_DIVERT))

    def _use_rift(self):
        sound.sfx("rift")
        if self.keepers:
            self.game.flags["escaped_keepers"] = True
            self.game.flags.save()
            self.game.pending_toasts.extend(self.game.flags.sync_achievements())
        if not self.quest_done:
            self.game.flags["defiance"] = self.game.flags["defiance"] + 1
            self.narrator.say(content.NARR_LEAVE)
        self.game.go("troi", destination="hub")

    def _get_caught(self):
        self.caught = True
        self.game.go("trapped", year=self.data["year"])

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
            obj = self._near()
            if obj:
                self._interact(obj)
        elif event.key == pygame.K_t:
            obj = self._near_takeable()
            if obj:
                self._take(obj)

    def update(self, dt):
        self.t += dt / 1000.0
        self.zone_t += dt / 1000.0
        self.achv_t += dt / 1000.0
        self.narrator.update(dt)
        self.dialogue.update(dt)
        self.particles.update(dt)
        for n in self.npcs:
            n.update(dt)

        if self.modal:
            sound.footsteps(False)
            self.modal.update(dt)
            if self.modal.done:
                result = self.modal.done
                self.modal = None
                if result == "success":
                    self._solve()
            return

        if self.dialogue.active or self.caught:
            sound.footsteps(False)
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self._solids(), self.world)
        sound.footsteps(self.player.moved_this_frame)

        pc = self.player.center()
        here = None
        for z in self.zones:
            if pygame.Rect(*z["rect"]).collidepoint(pc):
                here = z["name"]
                break
        if here and here != self.cur_zone:
            self.cur_zone = here
            self.zone_title = here
            self.zone_t = 0.0

        if self.flash > 0:
            self.flash = max(0.0, self.flash - dt / 600.0)

        if not self.quest_done and self.t > self.grace:
            rate = 1.4 * (1 + 0.3 * self.game.flags["instability"])
            self._raise_suspicion(dt / 1000.0 * rate)

        for k in self.keepers:
            k.update(pc, dt)
            if k.rect().inflate(-10, -10).colliderect(self.player.rect()):
                self._get_caught()
                return

    def draw(self, screen):
        cam = self._camera()
        screen.blit(self.floor, (-cam[0], -cam[1]))

        for w in self.walls:
            world.draw_prop(screen, "wall", w.move(-cam[0], -cam[1]), self.t, self.theme)

        near = None if self.dialogue.active else self._near()
        drawables = []
        for d in self.decor:
            drawables.append((d["rect"].bottom, "decor", d))
        for o in self.objects:
            if o.kind != "exit":
                drawables.append((o.base_y, "obj", o))
        for n in self.npcs:
            drawables.append((n.base_y, "npc", n))
        drawables.append((self.player.pos.y + PSIZE, "player", None))
        drawables.sort(key=lambda e: e[0])

        for _, kind, ref in drawables:
            if kind == "decor":
                world.draw_prop(screen, ref["kind"], ref["rect"].move(-cam[0], -cam[1]),
                                self.t, self.theme)
            elif kind == "obj":
                ref.draw(screen, cam, self.t, self.theme)
                self._interact_marker(screen, ref, cam, ref is near)
            elif kind == "npc":
                ref.draw(screen, cam, self.t, self.theme)
                self._interact_marker(screen, ref, cam, ref is near)
            else:
                self.player.draw(screen, *cam)

        if self.rift:
            self._draw_rift(screen, cam)

        for k in self.keepers:
            k.draw(screen, cam[0], cam[1])

        self.particles.draw(screen)
        world.draw_grade(screen, self.theme)
        world.draw_vignette(screen)

        if self.flash > 0:
            overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)
            overlay.fill((*config.BLOOD, int(120 * self.flash)))
            screen.blit(overlay, (0, 0))

        self._draw_hud(screen, near)
        self._draw_achievement_toast(screen)
        self.narrator.draw(screen)
        self.dialogue.draw(screen)

        if self.modal:
            self.modal.draw(screen)

    def _draw_achievement_toast(self, screen):
        ui.achievement_toast(screen, self.new_achievements, self.achv_t)

    def _interact_marker(self, screen, obj, cam, highlight):
        """A small, dim, uniform marker — there's *something* here, but nothing
        tells you which thing is the answer. Label + prompt only when you walk
        up to it. (No beacon leading you around.)"""
        pending_take = bool(obj.take and not self._taken(obj))
        if obj.kind != "exit" and obj.used and not pending_take \
                and not self._is_lock(obj):
            return

        r = obj.rect.move(-cam[0], -cam[1])
        bob = math.sin(self.t * 3 + r.x) * 3
        cx = r.centerx
        cy = r.top - 14 + bob
        pygame.draw.polygon(screen, config.DIM, [(cx, cy + 7), (cx - 5, cy), (cx + 5, cy)])
        if highlight:
            f = config.font(18)
            w = f.size(obj.label)[0]
            ui.panel(screen, pygame.Rect(cx - w // 2 - 12, r.top - 54, w + 24, 30),
                     fill=(10, 10, 14, 220), border=(70, 70, 82), accent=self.accent,
                     radius=8)
            ui.text(screen, f, obj.label, config.WHITE, cx, r.top - 48, center=True)
            if not self.dialogue.active:
                prompts = []
                if self._is_lock(obj) or not obj.used:
                    prompts.append(("[ E ]", config.WHITE))
                if pending_take:
                    prompts.append(("[ T ] take", config.WARN))
                px = cx - sum(config.font(15).size(p)[0] + 12 for p, _ in prompts) // 2
                for text, pc in prompts:
                    px += ui.text(screen, config.font(15), text, pc, px, r.bottom + 6) + 12

    def _draw_rift(self, screen, cam):
        r = self.rift.rect.move(-cam[0], -cam[1])
        ready = self.quest_done
        ring = config.RIFT if ready else (74, 92, 98)
        pulse = 0.5 + 0.5 * math.sin(self.t * 2.6)
        for i in range(6):
            rr = r.inflate(i * 16, i * 16)
            surf = pygame.Surface((rr.width, rr.height), pygame.SRCALPHA)
            a = int((110 if ready else 50) * pulse / (i + 1))
            pygame.draw.ellipse(surf, (*ring, a), surf.get_rect())
            screen.blit(surf, rr.topleft)
        pygame.draw.ellipse(screen, ring, r, 2)
        lbl = config.font(15).render("the rift" if ready else "rift (work unfinished)",
                                     True, ring)
        screen.blit(lbl, (r.centerx - lbl.get_width() // 2, r.bottom + 6))

    def _draw_hud(self, screen, near):
        ui.text(screen, config.font(26), self.data["year"], self.accent, 24, 12)

        if self.zone_title and self.zone_t < 3.4:
            a = 255 if self.zone_t < 2.2 else int(255 * (3.4 - self.zone_t) / 1.2)
            cy = config.HEIGHT // 2 - 80
            ui.text(screen, config.font(40), self.zone_title, config.WHITE,
                    config.WIDTH // 2, cy, center=True, alpha=a)
            ui.text(screen, config.font(16), "— %s —" % self.data["title"], config.ASH,
                    config.WIDTH // 2, cy + 48, center=True, alpha=a)

        if self.dialogue.active:
            return

        f = config.font(17)
        text = "Solved — find a rift to leave" if self.solved else self.puzzle["directive"]
        col = config.TITOR if self.solved else config.WHITE
        lines = wrap_text(text, f, 568)
        ph = 34 + len(lines) * 24
        panel = pygame.Rect(20, config.HEIGHT - 36 - ph, 600, ph)
        ui.panel(screen, panel, accent=self.accent)
        ui.text(screen, config.font(14), "DIRECTIVE", config.DIM,
                panel.x + 16, panel.y + 9)
        for i, line in enumerate(lines):
            ui.text(screen, f, line, col, panel.x + 16, panel.y + 30 + i * 24)

        satchel = self.game.flags["satchel"]
        if satchel:
            ui.text(screen, config.font(13), "SATCHEL:", config.WARN,
                    panel.x + 16, panel.bottom + 8, shadow=False)
            cx = panel.x + 92
            for item in satchel:
                cx += ui.chip(screen, config.font(14), item, config.BLOOD,
                              cx, panel.bottom + 4) + 8

        ui.text(screen, config.font(14), "WASD move · E interact · T take", config.DIM,
                config.WIDTH - 24, config.HEIGHT - 28, right=True, shadow=False)

        if self.suspicion > 1 and not self.quest_done:
            bw, bh = 220, 14
            bx, by = config.WIDTH - bw - 24, 30
            danger = self.suspicion >= 60
            ui.text(screen, config.font(15),
                    "KEEPERS NEAR" if danger else "ATTENTION",
                    config.WARN, bx + bw, by - 20, right=True)
            ui.bar(screen, pygame.Rect(bx, by, bw, bh),
                   self.suspicion / self.SUSPICION_MAX, config.WARN)
        instab = self.game.flags["instability"]
        if instab:
            ui.text(screen, config.font(13),
                    "INSTABILITY x%d — Keepers are restless" % instab,
                    config.BLOOD, config.WIDTH - 24, 52, right=True, shadow=False)
