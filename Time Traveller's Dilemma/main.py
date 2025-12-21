import pygame
from cutscene1 import Cutscene1
from player import Player

WIDTH, HEIGHT = 1000, 800
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Time Traveller's Dilemma")
clock = pygame.time.Clock()

font = pygame.font.Font("fonts/IBMPlexMono-Regular.ttf", 20)

cutscene = Cutscene1(screen, font, WIDTH, HEIGHT)
player = Player(screen, WIDTH, HEIGHT)

state = 'cutscene'
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if state == 'cutscene' and event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_RETURN
                and cutscene.done
                and not cutscene.fading_in
                and not cutscene.fading_out
            ):
                cutscene.advance()

    screen.fill((0, 0, 0))

    if state == 'cutscene':
        cutscene.update()
        cutscene.draw()
        if cutscene.finished():
            state = 'game'

    elif state == 'game':
        keys = pygame.key.get_pressed()
        player.update(keys)
        player.draw()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
