import pygame
from cutscene1 import Cutscene1
from player import Player
from timemachine import TimeMachine
from npc import NPC

def camera_offset(target_pos, screen_width, screen_height):
    return (
        int(target_pos.x - screen_width // 2),
        int(target_pos.y - screen_height // 2)
    )


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

npcs = []
npc_active = None

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

            if event.key == pygame.K_RETURN:
                if dialog_active:
                    dialog_active = False
                    interact_cooldown = 20
                elif npc_active:
                    npc_active.advance()
                    if not npc_active.active:
                        npc_active = None
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

        if not dialog_active and not npc_active:
            player.update(keys, [machine.rect])

        cam_x, cam_y = camera_offset(player.pos, WIDTH, HEIGHT)

        screen.blit(
            machine.image,
            (machine.rect.x - cam_x, machine.rect.y - cam_y)
        )

        if timeline == "past":
            for npc in npcs:
                npc.update()
                npc.draw(screen, cam_x, cam_y)

        player.draw(cam_x, cam_y)

        near_machine = player.rect().colliderect(machine.interact_rect)

        if timeline == "present" and near_machine and not dialog_active:
            prompt = font.render("Press E", True, (0, 0, 0))
            screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 + 90))

        if interact_pressed and not dialog_active and not npc_active and interact_cooldown == 0:
            if timeline == "present" and near_machine:
                fade_active = True
                fade_alpha = 0
                timeline = "past"

                px, py = player.pos
                npcs = [
                    NPC(1, px + 400, py - 200),
                    NPC(2, px - 600, py + 300),
                    NPC(3, px + 200, py + 500),
                    NPC(1, px - 300, py - 500),
                    NPC(2, px + 700, py + 100)
                ]

            elif timeline == "past":
                for npc in npcs:
                    if npc.try_interact(player.rect()):
                        npc_active = npc
                        break

                if near_machine and not npc_active:
                    dialog_active = True
                    dialog_counter = 0

        if npc_active:
            npc_active.draw_dialogue(screen, font, WIDTH, HEIGHT)

        if dialog_active:
            if dialog_counter < dialog_speed * len(dialog_text):
                dialog_counter += 1

            box = pygame.Surface((WIDTH - 200, 120))
            box.fill((40, 40, 40))
            screen.blit(box, (100, HEIGHT - 160))

            visible = dialog_text[: dialog_counter // dialog_speed]
            rendered = font.render(visible, True, (255, 255, 255))
            screen.blit(rendered, (120, HEIGHT - 120))

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
