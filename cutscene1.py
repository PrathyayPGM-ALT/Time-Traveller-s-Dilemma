import math
import random

import pygame

import config


class Cutscene1:
    """Opening: a few drifting thoughts, a red impact, then the boss reveals
    himself — silently, looming and swaying. He doesn't speak here; he speaks
    in the hub ("There you are... you wear that body so loosely"). Auto-plays;
    Esc skips.
    """

    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.WIDTH = width
        self.HEIGHT = height

        self.thoughts = [
            'Where... Where am I?',
            'The last thing I remember...',
            'The scientist...',
        ]

        self.phase = 'thoughts'
        self.active_thought = 0
        self.current_text = self.thoughts[0]
        self.counter = 0
        self.speed = 5
        self.t = 0.0

        self.pause_timer = 0
        self.pause_duration = 62

        self.impact_timer = 0
        self.impact_duration = 70

        self.black_timer = 0
        self.black_duration = 45

        self.hold_timer = 0
        self.hold_duration = 105

        self.alpha = 0
        self.fading_in = False
        self.fading_out = False
        self.fade_in_speed = 3
        self.fade_out_speed = 4

        self.shake_timer = 0
        self.shake_intensity = 20

        self.boss_img = pygame.image.load("textures/boss.png").convert_alpha()
        self.boss_img = pygame.transform.scale(self.boss_img, (160 * 2, 320 * 2))

    def update(self):
        self.t += 1 / 60.0
        if self.phase == 'thoughts':
            if self.counter < self.speed * len(self.current_text):
                self.counter += 1
            else:
                self.pause_timer += 1
                if self.pause_timer >= self.pause_duration:
                    self.pause_timer = 0
                    self.counter = 0
                    self.active_thought += 1
                    if self.active_thought < len(self.thoughts):
                        self.current_text = self.thoughts[self.active_thought]
                    else:
                        self.phase = 'impact'
                        self.impact_timer = self.impact_duration

        elif self.phase == 'impact':
            self.impact_timer -= 1
            if self.impact_timer <= 0:
                self.phase = 'black'
                self.black_timer = self.black_duration

        elif self.phase == 'black':
            self.black_timer -= 1
            if self.black_timer <= 0:
                self.phase = 'boss'
                self.fading_in = True

        elif self.phase == 'boss':
            if self.fading_in:
                self.alpha = min(255, self.alpha + self.fade_in_speed)
                if self.alpha >= 255:
                    self.fading_in = False
                    self.shake_timer = 22
            elif not self.fading_out:
                self.hold_timer += 1
                if self.hold_timer >= self.hold_duration:
                    self.fading_out = True
            if self.fading_out:
                self.alpha = max(0, self.alpha - self.fade_out_speed)
            if self.shake_timer > 0:
                self.shake_timer -= 1

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.phase == 'thoughts':
            text = self.current_text[0:self.counter // self.speed]
            snip = self.font.render(text, True, (190, 190, 190))
            self.screen.blit(snip, (self.WIDTH // 2 - snip.get_width() // 2,
                                    self.HEIGHT // 2))

        elif self.phase == 'impact':
            sx = random.randint(-self.shake_intensity, self.shake_intensity)
            sy = random.randint(-self.shake_intensity, self.shake_intensity)
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            intensity = int(200 * (self.impact_timer / self.impact_duration))
            pygame.draw.ellipse(overlay, (140, 0, 0, intensity),
                                (-self.WIDTH // 2, -self.HEIGHT // 2,
                                 self.WIDTH * 2, self.HEIGHT * 2))
            self.screen.blit(overlay, (sx, sy))

        elif self.phase == 'boss':
            shake = self.shake_timer > 0
            sx = random.randint(-9, 9) if shake else 0
            sy = random.randint(-9, 9) if shake else 0
            sway_x = math.sin(self.t * 1.1) * 5
            sway_y = math.sin(self.t * 0.8) * 4

            glow = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            gr = 160 + int(18 * math.sin(self.t * 1.6))
            pygame.draw.ellipse(glow, (60, 6, 8, int(80 * self.alpha / 255)),
                                (self.WIDTH // 2 - gr, 110, gr * 2, 420))
            self.screen.blit(glow, (0, 0))

            boss = self.boss_img.copy()
            boss.set_alpha(self.alpha)
            self.screen.blit(boss, (self.WIDTH // 2 - boss.get_width() // 2 + sx + sway_x,
                                    20 + sy + sway_y))

    def advance(self):
        if self.phase == 'boss' and not self.fading_in:
            self.fading_out = True

    def finished(self):
        return self.phase == 'boss' and self.fading_out and self.alpha == 0
