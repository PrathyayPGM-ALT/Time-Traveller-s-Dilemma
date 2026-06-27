"""Render scenes headlessly to PNGs so we can eyeball the visuals."""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame  # noqa
import scene  # noqa
from era import EraScene  # noqa
from troi import TroiScene  # noqa
from flow import TitleScene, TrappedScene  # noqa
import content  # noqa

scene.SAVE_PATH = "save.shot.json"
if os.path.exists(scene.SAVE_PATH):
    os.remove(scene.SAVE_PATH)

g = scene.Game()
g.flags.new_life()       # seed a life so procedural worlds generate
os.makedirs("shots", exist_ok=True)


def render(name, factory, frames=40, dt=40, setup=None, **kw):
    s = factory(g)
    g.scene = s
    s.on_enter(**kw)
    if setup:
        setup(s)
    for _ in range(frames):
        s.update(dt)
        s.draw(g.screen)
    pygame.image.save(g.screen, f"shots/{name}.png")
    print("saved", name)


def center_player(s):
    # drop the player into the middle zone so a 'place' fills the frame
    z = s.zones[1]["rect"]
    s.player.place(z[0] + z[2] // 2, z[1] + z[3] // 2)


from hub import HubScene  # noqa
render("title", TitleScene)
render("hub", HubScene)
render("troi", TroiScene, destination="hub")
render("trapped", TrappedScene, year="3744")
for k in content.ERA_ORDER:
    render("era_" + k.replace(" ", "_"), EraScene, setup=center_player, key=k)

# training scene
from training import TrainingScene  # noqa
render("training", TrainingScene)

if os.path.exists("save.shot.json"):
    os.remove("save.shot.json")
print("done")
