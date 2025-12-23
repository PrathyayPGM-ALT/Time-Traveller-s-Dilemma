import pygame

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


class NPC:
    DIALOGUE_SETS = {
        1: [
            "What's your name?",
            "Wait...",
            "I know that look.",
            "Haven't I seen you before?"
        ],
        2: [
            "You seem lost.",
            "This place has not changed in years.",
            "But you...",
            "You feel wrong."
        ],
        3: [
            "Sometimes I remember things that never happened.",
            "Faces I should not know.",
            "You are one of them."
        ]
    }

    def __init__(self, npc_id, x, y, scale=48):
        self.npc_id = npc_id

        self.image = pygame.transform.scale(
            pygame.image.load(f"textures/npc{npc_id}.png").convert_alpha(),
            (scale, scale)
        )

        self.portrait = pygame.transform.scale(
            pygame.image.load(f"textures/npc{npc_id}.png").convert_alpha(),
            (64, 64)
        )

        self.pos = pygame.Vector2(x, y)
        self.rect = pygame.Rect(x, y, scale, scale)
        self.interact_rect = self.rect.inflate(60, 60)

        self.dialogue = self.DIALOGUE_SETS[npc_id]
        self.line_index = 0

        self.active = False
        self.counter = 0
        self.speed = 3
        self.done = False

    def update(self):
        if self.active and not self.done:
            line = self.dialogue[self.line_index]
            if self.counter < self.speed * len(line):
                self.counter += 1
            else:
                self.done = True

    def draw(self, screen, cam_x, cam_y):
        screen.blit(
            self.image,
            (self.pos.x - cam_x, self.pos.y - cam_y)
        )

    def try_interact(self, player_rect):
        if not self.active and player_rect.colliderect(self.interact_rect):
            self.active = True
            self.line_index = 0
            self.counter = 0
            self.done = False
            return True
        return False

    def advance(self):
        if not self.done:
            return

        if self.line_index < len(self.dialogue) - 1:
            self.line_index += 1
            self.counter = 0
            self.done = False
        else:
            self.close()

    def close(self):
        self.active = False
        self.line_index = 0
        self.counter = 0
        self.done = False

    def draw_dialogue(self, screen, font, width, height):
        if not self.active:
            return

        box_width = width - 200
        box_height = 140
        box_x = 100
        box_y = height - 180

        box = pygame.Surface((box_width, box_height))
        box.fill((40, 40, 40))
        screen.blit(box, (box_x, box_y))

        portrait_bg = pygame.Surface((84, 84))
        portrait_bg.fill((30, 30, 30))
        screen.blit(portrait_bg, (box_x + 20, box_y + 28))
        screen.blit(self.portrait, (box_x + 30, box_y + 38))

        text_x = box_x + 120
        text_width = box_width - 150

        line = self.dialogue[self.line_index]
        visible = line[: self.counter // self.speed]
        lines = wrap_text(visible, font, text_width)

        y = box_y + 30
        for l in lines:
            rendered = font.render(l, True, (255, 255, 255))
            screen.blit(rendered, (text_x, y))
            y += font.get_height() + 4

        if self.done:
            prompt = font.render("Press Enter", True, (180, 180, 180))
            screen.blit(
                prompt,
                (box_x + box_width - prompt.get_width() - 20,
                 box_y + box_height - 30)
            )
