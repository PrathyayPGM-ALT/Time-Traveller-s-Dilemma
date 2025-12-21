import pygame, random

class Cutscene1:
    def __init__(self, screen, font, width, height):
        self.screen = screen
        self.font = font
        self.WIDTH = width
        self.HEIGHT = height

        self.thoughts = [
            'Where... Where am I?',
            'The last thing I remember...',
            'The scientist...'
        ]

        self.messages = [
            'You are conscious earlier than predicted.',
            'Do not move. This body is temporary.',
            'You were chosen because you hesitate.',
            'Others tried to win.',
            'YOU WILL TRY TO UNDERSTAND',
            'A timeline is collapsing.'
        ]

        self.phase = 'thoughts'
        self.active_thought = 0
        self.active_message = 0

        self.current_text = self.thoughts[self.active_thought]
        self.counter = 0
        self.speed = 5
        self.done = False

        self.pause_timer = 0
        self.pause_duration = 90

        self.impact_timer = 0
        self.impact_duration = 70

        self.black_timer = 0
        self.black_duration = 50

        self.alpha = 0
        self.fading_in = False
        self.fading_out = False
        self.fade_in_speed = 2
        self.fade_out_speed = 2

        self.shake_timer = 0
        self.shake_intensity = 20

        self.boss_img = pygame.image.load("textures/boss.png").convert_alpha()
        self.boss_img = pygame.transform.scale(self.boss_img, (128 * 3, 256 * 3))

        self.box_height = 120
        self.box_color = (0, 0, 0)
        self.box_alpha = 200

    def update(self):
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
                self.current_text = self.messages[self.active_message]
                self.counter = 0

        elif self.phase == 'boss':
            if self.fading_in:
                self.alpha += self.fade_in_speed
                if self.alpha >= 255:
                    self.alpha = 255
                    self.fading_in = False

            if self.fading_out:
                self.alpha -= self.fade_out_speed
                if self.alpha <= 0:
                    self.alpha = 0

            if self.current_text == 'YOU WILL TRY TO UNDERSTAND' and self.done and self.shake_timer == 0:
                self.shake_timer = 25

            if self.shake_timer > 0:
                self.shake_timer -= 1

    def draw(self):
        self.screen.fill((0, 0, 0))

        if self.phase == 'thoughts':
            text = self.current_text[0:self.counter // self.speed]
            snip = self.font.render(text, True, (190, 190, 190))
            self.screen.blit(
                snip,
                (self.WIDTH // 2 - snip.get_width() // 2, self.HEIGHT // 2)
            )

        elif self.phase == 'impact':
            shake_x = random.randint(-self.shake_intensity, self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity, self.shake_intensity)

            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            intensity = int(200 * (self.impact_timer / self.impact_duration))

            pygame.draw.ellipse(
                overlay,
                (140, 0, 0, intensity),
                (-self.WIDTH // 2, -self.HEIGHT // 2, self.WIDTH * 2, self.HEIGHT * 2)
            )

            self.screen.blit(overlay, (shake_x, shake_y))

        elif self.phase == 'boss':
            shake_x = random.randint(-10, 10) if self.shake_timer > 0 else 0
            shake_y = random.randint(-10, 10) if self.shake_timer > 0 else 0

            boss = self.boss_img.copy()
            boss.set_alpha(self.alpha)

            self.screen.blit(
                boss,
                (
                    self.WIDTH // 2 - boss.get_width() // 2 + shake_x,
                    20 + shake_y
                )
            )

            box_surface = pygame.Surface((self.WIDTH - 80, self.box_height))
            box_surface.set_alpha(self.box_alpha)
            box_surface.fill(self.box_color)

            self.screen.blit(
                box_surface,
                (40, self.HEIGHT - self.box_height - 40)
            )

            if not self.fading_in and not self.fading_out:
                if self.counter < self.speed * len(self.current_text):
                    self.counter += 1
                else:
                    self.done = True

            text = self.current_text[0:self.counter // self.speed]
            snip = self.font.render("Boss: " + text, True, (230, 230, 230))
            snip.set_alpha(self.alpha)

            self.screen.blit(
                snip,
                (60 + shake_x, self.HEIGHT - self.box_height + 10 + shake_y)
            )

    def advance(self):
        if self.phase != 'boss':
            return

        if self.active_message < len(self.messages) - 1:
            self.active_message += 1
            self.current_text = self.messages[self.active_message]
            self.counter = 0
            self.done = False
        else:
            self.fading_out = True

    def finished(self):
        return self.phase == 'boss' and self.alpha == 0 and self.fading_out
