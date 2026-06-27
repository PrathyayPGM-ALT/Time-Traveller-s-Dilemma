"""The player: top-down 4-direction movement with walk animation.

Scene-agnostic. Movement is clamped to world bounds and blocked by a list
of obstacle rects supplied each frame.
"""

import pygame

import assets

SIZE = 48


class Player:
    def __init__(self, x=0, y=0, speed=4):
        self.pos = pygame.Vector2(x, y)
        self.speed = speed

        self.alpha = 0
        self.fading_in = True
        self.fade_speed = 6

        def frames(name):
            return [assets.image(f"textures/player_{name}_1.png", (SIZE, SIZE)),
                    assets.image(f"textures/player_{name}_2.png", (SIZE, SIZE))]

        self.animations = {d: frames(d) for d in ("down", "up", "left", "right")}
        self.direction = "down"
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 9
        self.moved_this_frame = False

    def rect(self):
        return pygame.Rect(int(self.pos.x), int(self.pos.y), SIZE, SIZE)

    def center(self):
        return (self.pos.x + SIZE / 2, self.pos.y + SIZE / 2)

    def place(self, x, y):
        self.pos.update(x, y)

    def reset_fade_in(self):
        self.alpha = 0
        self.fading_in = True

    def update(self, keys, obstacles=(), bounds=None):
        if self.fading_in:
            self.alpha = min(255, self.alpha + self.fade_speed)
            if self.alpha >= 255:
                self.fading_in = False

        dx = dy = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx, self.direction = -self.speed, "left"
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx, self.direction = self.speed, "right"
        elif keys[pygame.K_w] or keys[pygame.K_UP]:
            dy, self.direction = -self.speed, "up"
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy, self.direction = self.speed, "down"

        self.moved_this_frame = bool(dx or dy)

        moved = self.rect().move(dx, 0)
        if not any(moved.colliderect(o) for o in obstacles):
            self.pos.x += dx
        moved = self.rect().move(0, dy)
        if not any(moved.colliderect(o) for o in obstacles):
            self.pos.y += dy

        if bounds is not None:
            self.pos.x = max(bounds.left, min(self.pos.x, bounds.right - SIZE))
            self.pos.y = max(bounds.top, min(self.pos.y, bounds.bottom - SIZE))

        if self.moved_this_frame:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % 2
        else:
            self.frame = 0

    def draw(self, screen, cam_x=0, cam_y=0):
        sx, sy = self.pos.x - cam_x, self.pos.y - cam_y
        shadow = pygame.Surface((SIZE - 14, SIZE // 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), shadow.get_rect())
        screen.blit(shadow, (sx + 7, sy + SIZE - SIZE // 7))
        sprite = self.animations[self.direction][self.frame].copy()
        sprite.set_alpha(self.alpha)
        screen.blit(sprite, (sx, sy))
