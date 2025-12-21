import pygame

class Player:
    def __init__(self, screen, width, height):
        self.screen = screen
        self.WIDTH = width
        self.HEIGHT = height

        self.pos = pygame.Vector2(width // 2, height // 2)
        self.speed = 5

        self.alpha = 0
        self.fading_in = True
        self.fade_speed = 3

        self.animations = {
            'down': [
                pygame.transform.scale(pygame.image.load('textures/player_down1.png').convert_alpha(), (64, 64)),
                pygame.transform.scale(pygame.image.load('textures/player_down2.png').convert_alpha(), (64, 64))
            ],
            'up': [
                pygame.transform.scale(pygame.image.load('textures/player_up1.png').convert_alpha(), (64, 64)),
                pygame.transform.scale(pygame.image.load('textures/player_up2.png').convert_alpha(), (64, 64))
            ],
            'left': [
                pygame.transform.scale(pygame.image.load('textures/player_left1.png').convert_alpha(), (64, 64)),
                pygame.transform.scale(pygame.image.load('textures/player_left2.png').convert_alpha(), (64, 64))
            ],
            'right': [
                pygame.transform.scale(pygame.image.load('textures/player_right1.png').convert_alpha(), (64, 64)),
                pygame.transform.scale(pygame.image.load('textures/player_right2.png').convert_alpha(), (64, 64))
            ]
        }

        self.direction = 'down'
        self.frame = 0
        self.frame_timer = 0
        self.frame_speed = 10

    def update(self, keys):
        if self.fading_in:
            self.alpha += self.fade_speed
            if self.alpha >= 255:
                self.alpha = 255
                self.fading_in = False

        moving = False

        if keys[pygame.K_a]:
            self.pos.x -= self.speed
            self.direction = 'left'
            moving = True
        elif keys[pygame.K_d]:
            self.pos.x += self.speed
            self.direction = 'right'
            moving = True
        elif keys[pygame.K_w]:
            self.pos.y -= self.speed
            self.direction = 'up'
            moving = True
        elif keys[pygame.K_s]:
            self.pos.y += self.speed
            self.direction = 'down'
            moving = True

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
