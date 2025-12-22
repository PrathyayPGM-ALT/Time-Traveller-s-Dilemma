import pygame

class Player:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height

        self.pos = pygame.Vector2(width // 2 - 100, height // 2)
        self.speed = 4

        self.alpha = 0
        self.fading_in = True
        self.fade_speed = 4

        self.animations = {
            'down': [
                pygame.transform.scale(pygame.image.load('textures/player_down_1.png').convert_alpha(), (32, 32)),
                pygame.transform.scale(pygame.image.load('textures/player_down_2.png').convert_alpha(), (32, 32))
            ],
            'up': [
                pygame.transform.scale(pygame.image.load('textures/player_up_1.png').convert_alpha(), (32, 32)),
                pygame.transform.scale(pygame.image.load('textures/player_up_2.png').convert_alpha(), (32, 32))
            ],
            'left': [
                pygame.transform.scale(pygame.image.load('textures/player_left_1.png').convert_alpha(), (32, 32)),
                pygame.transform.scale(pygame.image.load('textures/player_left_2.png').convert_alpha(), (32, 32))
            ],
            'right': [
                pygame.transform.scale(pygame.image.load('textures/player_right_1.png').convert_alpha(), (32, 32)),
                pygame.transform.scale(pygame.image.load('textures/player_right_2.png').convert_alpha(), (32, 32))
            ]
        }

        self.direction = 'down'
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 12

    def rect(self):
        return pygame.Rect(self.pos.x, self.pos.y, 32, 32)

    def reset_fade_in(self):
        self.alpha = 0
        self.fading_in = True

    def update(self, keys, obstacles):
        if self.fading_in:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_in = False

        dx = dy = 0
        moving = False

        if keys[pygame.K_a]:
            dx -= self.speed
            self.direction = 'left'
            moving = True
        elif keys[pygame.K_d]:
            dx += self.speed
            self.direction = 'right'
            moving = True
        elif keys[pygame.K_w]:
            dy -= self.speed
            self.direction = 'up'
            moving = True
        elif keys[pygame.K_s]:
            dy += self.speed
            self.direction = 'down'
            moving = True

        new_rect = self.rect().move(dx, 0)
        if not any(new_rect.colliderect(o) for o in obstacles):
            self.pos.x += dx

        new_rect = self.rect().move(0, dy)
        if not any(new_rect.colliderect(o) for o in obstacles):
            self.pos.y += dy

        if moving:
            self.frame_timer += 1
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.frame = (self.frame + 1) % 2
        else:
            self.frame = 0

        self.pos.x = max(0, min(self.WIDTH - 32, self.pos.x))
        self.pos.y = max(0, min(self.HEIGHT - 32, self.pos.y))

    def draw(self):
        sprite = self.animations[self.direction][self.frame].copy()
        sprite.set_alpha(self.alpha)
        self.screen.blit(sprite, self.pos)
