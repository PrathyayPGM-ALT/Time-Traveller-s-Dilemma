"""Scene base class and the Game / scene-manager core."""

import asyncio
import json
import os
import random

import pygame

import config
import sound

SAVE_PATH = "save.json"


class Scene:
    capturing_text = False      # True when a scene wants raw keystrokes (e.g. a terminal)

    def __init__(self, game):
        self.game = game

    def on_enter(self, **kwargs):
        pass

    def on_exit(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class Flags:
    """Two layers of state, saved together.

    SOUL keys persist across "New Game" — the player thinks each start is
    fresh, but the soul remembers. RUN keys describe the current life and
    are wiped when a new life begins.
    """

    SOUL = {
        "lives": 0,             # incarnations begun
        "echoes": [],           # short memories of past lives
        "total_quests": 0,      # eras completed across all lives
        "total_caught": 0,      # times the Keepers took a life
        "ever_eras": [],        # eras ever completed in any life
        "ending_seen": False,   # has the loop ever closed
        "trained": False,       # has the boss run orientation (ever)
        "achievements": [],     # unlocked achievement ids (permanent)
        "escaped_keepers": False,  # ever fled a timeline with Keepers on you
    }
    RUN = {
        "intro_seen": False,
        "eras_done": [],        # eras completed this life
        "visits": 0,            # Troi crossings this life
        "titor_truth": False,
        "defiance": 0,
        "run_seed": 0,          # seeds procedural worlds for this life
        "run_ended": False,     # life is over (trapped or loop closed)
        "satchel": [],          # items carried between timelines (contraband)
        "instability": 0,       # how much you've torn — angers the Keepers
    }
    MAX_ECHOES = 24

    def __init__(self):
        self.data = {**self.SOUL, **self.RUN}
        self.load()
        self.sync_achievements()    # retroactively unlock from existing progress

    def __getitem__(self, k):
        return self.data.get(k)

    def __setitem__(self, k, v):
        self.data[k] = v

    def done(self, era):
        return era in self.data["eras_done"]

    def complete(self, era):
        if era not in self.data["eras_done"]:
            self.data["eras_done"].append(era)
        if era not in self.data["ever_eras"]:   # the soul remembers immediately
            self.data["ever_eras"].append(era)

    def sync_achievements(self):
        """Unlock any achievements whose conditions are now met.

        Returns the list of newly-unlocked achievement dicts (for a toast).
        """
        import content
        new = []
        for a in content.ACHIEVEMENTS:
            if a["id"] not in self.data["achievements"] and a["check"](self):
                self.data["achievements"].append(a["id"])
                new.append(a)
        if new:
            self.save()
        return new

    # -- life cycle ------------------------------------------------------
    def has_run(self):
        d = self.data
        return not d["run_ended"] and (d["intro_seen"] or d["visits"] > 0
                                       or d["eras_done"])

    def _fold(self, text):
        self.data["echoes"].append(text)
        self.data["echoes"] = self.data["echoes"][-self.MAX_ECHOES:]

    def _summary(self):
        d = self.data
        n = len(d["eras_done"])
        life = d["lives"]
        if n == 0:
            return f"Life {life}: woke, wandered, and abandoned the work."
        years = ", ".join(d["eras_done"])
        if d["defiance"] >= 3:
            return f"Life {life}: did the work in {years}, but kept wandering off."
        return f"Life {life}: quietly finished {years} and asked no questions."

    def new_life(self):
        """Begin a new incarnation. The soul carries over; the life resets."""
        d = self.data
        if self.has_run():
            self._fold(self._summary())
            d["total_quests"] += len(d["eras_done"])
            for e in d["eras_done"]:
                if e not in d["ever_eras"]:
                    d["ever_eras"].append(e)
        d["lives"] += 1
        d["run_seed"] = random.randint(1, 2_000_000_000)
        d["intro_seen"] = False
        d["eras_done"] = []
        d["visits"] = 0
        d["titor_truth"] = False
        d["defiance"] = 0
        d["run_ended"] = False
        d["satchel"] = []
        d["instability"] = 0
        self.save()

    def mark_trapped(self, year):
        d = self.data
        if not d["run_ended"]:
            self._fold(f"Life {d['lives']}: taken by the Keepers in {year}. "
                       "It never woke again.")
            d["total_caught"] += 1
            d["run_ended"] = True
            self.save()

    def mark_ending(self):
        d = self.data
        if not d["run_ended"]:
            self._fold(f"Life {d['lives']}: closed the loop and saw its own face "
                       "in the fire.")
            d["ending_seen"] = True
            d["run_ended"] = True
            self.save()

    def load(self):
        if os.path.exists(SAVE_PATH):
            try:
                with open(SAVE_PATH, "r", encoding="utf-8") as f:
                    self.data.update(json.load(f))
            except (OSError, ValueError):
                pass

    def save(self):
        try:
            with open(SAVE_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
        except OSError:
            pass


class Game:
    FADE_SPEED = 14

    def __init__(self):
        # Create the display FIRST. On web (pygbag/WASM) audio init can stall,
        # and if that happened before set_mode the canvas never sized and the
        # page hung on grey. Display-first guarantees the window comes up.
        pygame.init()
        print("BOOT: pygame.init done")
        pygame.display.set_caption(config.TITLE)
        self.screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        print("BOOT: display up")

        sound.init()
        sound.ambience()          # persistent creepy bed under every scene
        print("BOOT: audio init done")

        self.flags = Flags()
        self._registry = {}
        self.scene = None
        self.pending_toasts = []     # achievements unlocked mid-transition
        print("BOOT: flags ready")

        # transition state
        self._next = None
        self._fade = 0
        self._fade_dir = 0          # +1 = fading out, -1 = fading in

    def register(self, name, factory):
        self._registry[name] = factory

    def go(self, name, fade=True, **kwargs):
        if not fade:
            self._swap(name, kwargs)
            return
        self._next = (name, kwargs)
        self._fade_dir = 1

    @property
    def transitioning(self):
        return self._fade_dir == 1

    def _swap(self, name, kwargs):
        sound.stop_footsteps()
        if self.scene:
            self.scene.on_exit()
        self.scene = self._registry[name](self)
        self.scene.on_enter(**kwargs)

    def _tick_transition(self):
        if self._fade_dir == 0:
            return
        self._fade += self._fade_dir * self.FADE_SPEED
        if self._fade >= 255 and self._fade_dir == 1:
            self._fade = 255
            name, kwargs = self._next
            self._next = None
            self._swap(name, kwargs)
            self._fade_dir = -1
        elif self._fade <= 0 and self._fade_dir == -1:
            self._fade = 0
            self._fade_dir = 0

    def _draw_transition(self):
        if self._fade <= 0:
            return
        overlay = pygame.Surface((config.WIDTH, config.HEIGHT))
        overlay.set_alpha(self._fade)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

    async def run(self, start):
        """The main loop. Async so it also runs under pygbag (web/WASM),
        which needs the loop to yield to the browser once per frame."""
        self._swap(start, {})
        while self.running:
            dt = self.clock.tick(config.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F4 \
                        and event.mod & pygame.KMOD_ALT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_m \
                        and not getattr(self.scene, "capturing_text", False):
                    sound.toggle()           # mute / unmute audio
                elif not self.transitioning:
                    self.scene.handle_event(event)

            self.scene.update(dt)
            self.scene.draw(self.screen)
            self._tick_transition()
            self._draw_transition()
            pygame.display.flip()
            await asyncio.sleep(0)            # hand control back to the browser

        self.flags.save()
        pygame.quit()
