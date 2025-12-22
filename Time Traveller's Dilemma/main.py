import pygame
from cutscene1 import Cutscene1
from player import Player
from timemachine import TimeMachine

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + word + " "
        if font.size(test)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = word + " "

    lines.append(current)
    return lines


WIDTH, HEIGHT = 1000, 800
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Time Traveller's Dilemma")
clock = pygame.time.Clock()

font = pygame.font.Font("fonts/IBMPlexMono-Regular.ttf", 20)

cutscene = Cutscene1(screen, font, WIDTH, HEIGHT)
player = Player(screen, WIDTH, HEIGHT)
machine = TimeMachine(WIDTH, HEIGHT)

state = "cutscene"
timeline = "present"

fade_alpha = 0
fade_active = False

interact_pressed = False
interact_cooldown = 0

dialog_active = False
dialog_text = "It seems to be malfunctioning. You need to complete the mission to travel back to the future."
dialog_counter = 0
dialog_speed = 3

running = True
while running:
    interact_pressed = False

    if interact_cooldown > 0:
        interact_cooldown -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if state == "cutscene" and event.key == pygame.K_RETURN:
                cutscene.advance()

            if event.key == pygame.K_e:
                interact_pressed = True

            if event.key == pygame.K_RETURN and dialog_active:
                dialog_active = False
                interact_cooldown = 20

    if state == "cutscene":
        screen.fill((0, 0, 0))
        cutscene.update()
        cutscene.draw()

        if cutscene.finished():
            state = "game"
            timeline = "present"
            player.reset_fade_in()

    elif state == "game":
        bg = (255, 255, 255) if timeline == "present" else (0, 0, 0)
        screen.fill(bg)

        keys = pygame.key.get_pressed()

        if not dialog_active:
            player.update(keys, [machine.rect])

        machine.draw(screen)
        player.draw()

        near_machine = player.rect().colliderect(machine.interact_rect)

        if near_machine and not dialog_active:
            prompt_color = (0, 0, 0) if timeline == "present" else (255, 255, 255)
            prompt = font.render("Press E", True, prompt_color)
            screen.blit(
                prompt,
                (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 90)
            )

        if interact_pressed and near_machine and not dialog_active and interact_cooldown == 0:
            if timeline == "present":
                fade_active = True
                fade_alpha = 0
                timeline = "past"
            else:
                dialog_active = True
                dialog_counter = 0

        if dialog_active:
            if dialog_counter < dialog_speed * len(dialog_text):
                dialog_counter += 1

            box_width = WIDTH - 200
            box_height = 120
            box_x = 100
            box_y = HEIGHT - 160

            box = pygame.Surface((box_width, box_height))
            box.fill((40, 40, 40))
            screen.blit(box, (box_x, box_y))

            visible_text = dialog_text[:dialog_counter // dialog_speed]
            lines = wrap_text(visible_text, font, box_width - 40)

            y = box_y + 20
            for line in lines:
                rendered = font.render(line, True, (255, 255, 255))
                screen.blit(rendered, (box_x + 20, y))
                y += font.get_height() + 4

    if fade_active:
        fade_alpha += 8
        if fade_alpha >= 255:
            fade_alpha = 255
            fade_active = False
            player.reset_fade_in()

        fade = pygame.Surface((WIDTH, HEIGHT))
        fade.set_alpha(fade_alpha)
        fade.fill((0, 0, 0))
        screen.blit(fade, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
