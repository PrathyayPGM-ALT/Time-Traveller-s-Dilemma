"""Render curated promo screenshots for the itch page -> promo/*.png"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa
import scene  # noqa
from flow import TitleScene, TrappedScene  # noqa
from hub import HubScene  # noqa
from troi import TroiScene  # noqa
from era import EraScene  # noqa
from codelock import CodeLockModal  # noqa

scene.SAVE_PATH = "save.promo.json"
if os.path.exists(scene.SAVE_PATH):
    os.remove(scene.SAVE_PATH)

g = scene.Game()
g.flags.new_life()
os.makedirs("promo", exist_ok=True)


def steps(s, n, dt=30):
    for _ in range(n):
        s.update(dt)
        s.draw(g.screen)


def save(name):
    pygame.image.save(g.screen, f"promo/{name}.png")
    print("saved", name)


# 1. title
t = TitleScene(g); g.scene = t; t.on_enter(); steps(t, 30); save("01_title")

# 2. hub — the boss, first line typed
h = HubScene(g); g.scene = h; h.on_enter(); steps(h, 110); save("02_boss")

# 3. the Troi
tr = TroiScene(g); g.scene = tr; tr.on_enter(destination="hub"); steps(tr, 70); save("03_troi")


def era_shot(key, name, center=True):
    e = EraScene(g); g.scene = e; e.on_enter(key=key)
    if center:
        z = e.zones[1]["rect"]
        e.player.place(z[0] + z[2] // 2, z[1] + z[3] // 2)
    steps(e, 40)            # fade in + zone card still up
    save(name)
    return e

# 4-5. eras
era_shot("24567 BC", "04_cave")
era_shot("1683", "05_observatory")
era_shot("2001", "06_cafe")

# 7. the code-lock puzzle (on the cave's figure)
e = EraScene(g); g.scene = e; e.on_enter(key="24567 BC")
lock = next(o for o in e._interactables() if o.id == e.lock_id)
e._interact(lock)
e.modal.input = "y"
steps(e, 6)
save("07_puzzle")

# 8. trapped
tp = TrappedScene(g); g.scene = tp; tp.on_enter(year="3744"); steps(tp, 50); save("08_trapped")

if os.path.exists("save.promo.json"):
    os.remove("save.promo.json")
print("done")
