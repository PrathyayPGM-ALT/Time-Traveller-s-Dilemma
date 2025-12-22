import pygame

class TimeMachine:
    def __init__(self, width, height):
        self.image = pygame.transform.scale(
            pygame.image.load("textures/time_machine.png").convert_alpha(),
            (64, 64)
        )
        self.rect = self.image.get_rect(center=(width // 2 + 80, height // 2))
        self.interact_rect = self.rect.inflate(40, 40)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
