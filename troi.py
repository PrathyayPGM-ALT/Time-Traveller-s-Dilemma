"""The Troi: the void you pass through on every jump.

Familiar figures drift here, half-remembered. Whispers surface and fade.
Walk into the rift to continue to your destination. The longer your journey,
the more figures float — always one more than before.
"""

import math
import random

import pygame

import config
import assets
import content
import sound
from scene import Scene
from player import Player
from narrator import Narrator


class Floater:
    SPRITES = ["textures/npc1.png", "textures/npc2.png",
               "textures/npc3.png", "textures/boss.png"]

    def __init__(self, idx, w, h):
        path = self.SPRITES[idx % len(self.SPRITES)]
        size = (54, 54) if "boss" not in path else (60, 96)
        self.image = assets.tinted(path, size, config.ASH, 70)
        self.pos = pygame.Vector2(random.randint(80, w - 80),
                                  random.randint(120, h - 160))
        self.vel = pygame.Vector2(random.uniform(-0.3, 0.3),
                                  random.uniform(-0.3, 0.3))
        self.phase = random.random() * math.tau
        self.w, self.h = w, h

    def update(self, dt):
        self.phase += dt / 600.0
        self.pos += self.vel
        if self.pos.x < 40 or self.pos.x > self.w - 40:
            self.vel.x *= -1
        if self.pos.y < 100 or self.pos.y > self.h - 120:
            self.vel.y *= -1

    def draw(self, screen):
        bob = math.sin(self.phase) * 8
        a = int(50 + 30 * (0.5 + 0.5 * math.sin(self.phase * 0.7)))
        img = self.image.copy()
        img.set_alpha(a)
        screen.blit(img, (self.pos.x, self.pos.y + bob))


class Whisper:
    def __init__(self, text, w, h):
        self.text = text
        self.surf = config.font(19).render(text, True, config.ASH)
        self.pos = (random.randint(60, w - self.surf.get_width() - 60),
                    random.randint(140, h - 200))
        self.age = 0.0
        self.life = random.uniform(4.0, 7.0)

    def update(self, dt):
        self.age += dt / 1000.0
        return self.age < self.life

    def draw(self, screen):
        # fade in then out over its life
        f = min(self.age / 1.2, (self.life - self.age) / 1.2, 1.0)
        a = max(0, int(150 * f))
        s = self.surf.copy()
        s.set_alpha(a)
        screen.blit(s, self.pos)


class TroiScene(Scene):
    def on_enter(self, destination="hub"):
        sound.music("troi")
        self.destination = destination
        w, h = config.WIDTH, config.HEIGHT

        self.game.flags["visits"] = self.game.flags["visits"] + 1
        visits = self.game.flags["visits"]

        self.player = Player(w // 2 - 18, h - 160, speed=3)
        self.player.reset_fade_in()

        # more figures the more you have crossed — across this life and all lives
        n = content.troi_floaters(self.game.flags)
        self.floaters = [Floater(i, w, h) for i in range(n)]
        self.whisper_pool = content.troi_whispers(self.game.flags)

        self.rift = pygame.Rect(w // 2 - 55, 150, 110, 110)
        self.whispers = []
        self.whisper_timer = 0.0
        self.t = 0.0

        self.narrator = Narrator()
        first = visits == 1 and self.game.flags["lives"] <= 1
        self.narrator.say(content.TROI_FIRST if first else content.TROI_LATER)

    def handle_event(self, event):
        pass

    def update(self, dt):
        self.t += dt / 1000.0
        self.narrator.update(dt)

        keys = pygame.key.get_pressed()
        bounds = pygame.Rect(20, 100, config.WIDTH - 40, config.HEIGHT - 120)
        self.player.update(keys, (), bounds)
        sound.footsteps(self.player.moved_this_frame)

        for f in self.floaters:
            f.update(dt)

        self.whisper_timer += dt / 1000.0
        if self.whisper_timer > 1.6 and len(self.whispers) < 4:
            self.whisper_timer = 0.0
            self.whispers.append(Whisper(random.choice(self.whisper_pool),
                                         config.WIDTH, config.HEIGHT))
        self.whispers = [w for w in self.whispers if w.update(dt)]

        if self.player.rect().colliderect(self.rift.inflate(-10, -10)):
            sound.sfx("rift")
            if self.destination == "hub":
                self.game.go("hub")
            else:
                self.game.go("era", key=self.destination)

    def draw(self, screen):
        screen.fill((6, 7, 12))
        # faint drifting starfield-ish dust
        for i in range(40):
            x = int((i * 137 + self.t * 12) % config.WIDTH)
            y = int((i * 89 + self.t * 5) % config.HEIGHT)
            screen.set_at((x, y), (24, 26, 34))

        for w in self.whispers:
            w.draw(screen)
        for f in self.floaters:
            f.draw(screen)

        # the rift
        pulse = 0.5 + 0.5 * math.sin(self.t * 2.5)
        for i in range(6):
            rr = self.rift.inflate(i * 18, i * 18)
            surf = pygame.Surface((rr.width, rr.height), pygame.SRCALPHA)
            a = int(120 * pulse / (i + 1))
            pygame.draw.ellipse(surf, (*config.RIFT, a), surf.get_rect())
            screen.blit(surf, rr.topleft)
        pygame.draw.ellipse(screen, config.RIFT, self.rift, 2)

        lbl = config.font(16).render("the rift", True, config.RIFT)
        screen.blit(lbl, (self.rift.centerx - lbl.get_width() // 2, self.rift.bottom + 10))

        self.player.draw(screen)
        self.narrator.draw(screen)

        title = config.font(20).render("THE TROI", True, config.DIM)
        screen.blit(title, (config.WIDTH // 2 - title.get_width() // 2, 24))
