"""Time Keepers: figures that wake when your suspicion peaks and hunt you.

If one touches you, you are dragged back to the Troi — forever.
"""

import math
import random

import pygame

import config
import assets

SIZE = 46


class TimeKeeper:
    def __init__(self, x, y, speed=2.5):
        self.pos = pygame.Vector2(x, y)
        self.speed = speed
        self.image = assets.tinted("textures/npc2.png", (SIZE, SIZE), config.WARN, 235)
        self.phase = random.random() * math.tau

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), SIZE, SIZE)

    def update(self, target_center, dt):
        self.phase += dt / 200.0
        d = pygame.Vector2(target_center) - (self.pos + pygame.Vector2(SIZE / 2, SIZE / 2))
        if d.length_squared() > 1:
            self.pos += d.normalize() * self.speed

    def draw(self, screen, cam_x, cam_y):
        sx, sy = self.pos.x - cam_x, self.pos.y - cam_y
        glow_r = int(SIZE * 0.9 + math.sin(self.phase) * 5)
        glow = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*config.WARN, 60), (glow_r, glow_r), glow_r)
        screen.blit(glow, (sx + SIZE / 2 - glow_r, sy + SIZE / 2 - glow_r))
        screen.blit(self.image, (sx, sy))
