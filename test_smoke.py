"""Headless smoke test: drive every scene, exercise dialogue/interaction/keepers.

Run: python test_smoke.py   (uses SDL dummy drivers, opens no window)
"""

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

import scene
from flow import (TitleScene, IntroScene, TrappedScene, EndingScene,
                  AchievementsScene)
from hub import HubScene
from troi import TroiScene
from era import EraScene
from training import TrainingScene
from terminal import TerminalModal
import content

scene.SAVE_PATH = "save.test.json"
if os.path.exists("save.test.json"):
    os.remove("save.test.json")

game = scene.Game()
for name, factory in [("title", TitleScene), ("intro", IntroScene),
                      ("hub", HubScene), ("troi", TroiScene),
                      ("era", EraScene), ("training", TrainingScene),
                      ("trapped", TrappedScene), ("ending", EndingScene),
                      ("achievements", AchievementsScene)]:
    game.register(name, factory)


def key(k):
    game.scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0))


def term_type(modal, s):
    for ch in s:
        modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=0, unicode=ch, mod=0))


def term_key(modal, k):
    modal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k, unicode="", mod=0))


def step(n=1, dt=50):
    for _ in range(n):
        game.scene.update(dt)
        game.scene.draw(game.screen)
        game._tick_transition()


def settle():
    for _ in range(60):
        step()
        if not game.transitioning:
            break


def drain_dialogue(maxi=400):
    for _ in range(maxi):
        if not getattr(game.scene, "dialogue", None) or not game.scene.dialogue.active:
            return
        step()
        key(pygame.K_RETURN)
    raise RuntimeError("dialogue never drained")


checks = []


def expect(cond, msg):
    checks.append((bool(cond), msg))
    print(("OK  " if cond else "FAIL") + "  " + msg)


game._swap("title", {})
step(5)
expect(isinstance(game.scene, TitleScene), "title scene loads")
key(pygame.K_RETURN)
settle()
expect(isinstance(game.scene, IntroScene), "title -> intro")
game.flags["trained"] = True

for _ in range(6000):
    step()
    if isinstance(game.scene, HubScene):
        break
expect(isinstance(game.scene, HubScene), "intro -> hub")

drain_dialogue()
expect(not game.scene.menu_locked, "hub menu unlocks after boss intro")
expect(game.flags["intro_seen"], "intro_seen set after boss intro")
game.scene.selected = next(i for i, (eid, _) in enumerate(game.scene.entries)
                           if eid == "2001")
key(pygame.K_RETURN)
drain_dialogue()
settle()
expect(isinstance(game.scene, TroiScene), "hub -> troi (to 2001)")
expect(game.flags["visits"] == 1, "first Troi visit counted")

troi = game.scene
troi.player.place(troi.rift.centerx - 18, troi.rift.centery - 18)
step(3)
settle()
expect(isinstance(game.scene, EraScene) and game.scene.key == "2001",
       "troi -> era 2001")

era = game.scene


def find(scene, oid):
    return next(o for o in scene._interactables() if o.id == oid)


expect(era.rift is not None, "procedural layout has a rift")
expect(len(era.walls) > 0 and len(era.zones) >= 4, "procedural rooms generated")
expect(era.lock_id == "terminal", "2001's lock is the terminal")

notice = find(era, "notice")
era._interact(notice)
drain_dialogue()
expect(notice.used, "a clue can be read")

lock = find(era, era.lock_id)
era._interact(lock)
expect(era.modal is not None, "the lock opens a code-entry puzzle")
before = era.suspicion
term_type(era.modal, "0000")
term_key(era.modal, pygame.K_RETURN)
expect(era.suspicion > before, "a wrong code raises attention")

term_type(era.modal, "2036")
term_key(era.modal, pygame.K_RETURN)
for _ in range(80):
    era.update(50)
    if era.modal is None:
        break
expect(era.solved, "the right code solves the era")
expect(game.flags.done("2001"), "2001 marked complete in flags")
expect("titor" in game.flags["achievements"], "beating 2001 unlocks an achievement")
expect(era.new_achievements, "the era queues an unlock toast")

era2 = EraScene(game)
era2.on_enter(key="3744")
game.scene = era2
lore = next(o for o in era2._interactables() if getattr(o, "risky", False))
era2._interact(lore)
drain_dialogue()
expect(era2.suspicion > 0, "risky interaction raises suspicion")

take_obj = next((o for o in era2.objects if getattr(o, "take", None)), None)
expect(take_obj is not None, "era has a takeable item")
bi = game.flags["instability"]
era2._take(take_obj)
expect(take_obj.take in game.flags["satchel"], "taking adds the item to the satchel")
expect(game.flags["instability"] == bi + 1, "taking raises instability")

era2._raise_suspicion(100)
expect(len(era2.keepers) >= 3, "contraband -> peak spawns extra Keepers")

era2.keepers[0].pos.update(era2.player.pos)
step(2)
settle()
expect(isinstance(game.scene, TrappedScene), "-> trapped scene")
expect(game.flags["run_ended"], "trapped ends the run")
expect(game.flags["total_caught"] >= 1, "soul records the catch")
trapped = game.scene
key(pygame.K_RETURN)
step(3)
expect(isinstance(game.scene, TrappedScene), "Enter does not free you from the Troi")
if trapped.beings:
    b = trapped.beings[0]
    trapped.player.place(int(b["f"].pos.x) + 9, int(b["f"].pos.y) + 9)
    step(2)
    key(pygame.K_e)
    step(2)
    expect(trapped.dialogue.active, "can converse with a being in the trap")

lives_before = game.flags["lives"]
game.flags.new_life()
expect(game.flags["lives"] == lives_before + 1, "new life increments incarnations")
expect(game.flags["eras_done"] == [], "new life resets run progress")
expect(game.flags["satchel"] == [] and game.flags["instability"] == 0,
       "new life empties the satchel")
expect(not game.flags["run_ended"], "new life clears run_ended")
expect(game.flags["run_seed"] != 0, "new life seeds a fresh world")

game.flags["intro_seen"] = True
for k in content.ERA_ORDER:
    game.flags.complete(k)
game._swap("hub", {})
drain_dialogue()
settle()
expect(isinstance(game.scene, EndingScene), "all-done hub -> ending")
expect(game.flags["run_ended"], "ending ends the run")
step(5)
key(pygame.K_RETURN)
step(200)
key(pygame.K_RETURN)
settle()
expect(isinstance(game.scene, TitleScene), "ending -> title")

new = game.flags.sync_achievements()
unlocked = game.flags["achievements"]
for aid in ("titor", "ibm", "forbidden", "theboss", "theend"):
    expect(aid in unlocked, "achievement '%s' unlocked after finishing all eras" % aid)

game._swap("achievements", {})
step(3)
expect(isinstance(game.scene, AchievementsScene), "achievements scene loads")
key(pygame.K_ESCAPE)
settle()
expect(isinstance(game.scene, TitleScene), "achievements -> title on Esc")
expect(set(unlocked) == set(scene.Flags().data["achievements"]),
       "achievements persist in the saved soul")

game.flags.new_life()
game.flags["escaped_keepers"] = False
if "panic" in game.flags["achievements"]:
    game.flags["achievements"].remove("panic")
pe = EraScene(game)
pe.on_enter(key="2001")
game.scene = pe
pe._raise_suspicion(100)
expect(len(pe.keepers) > 0, "high suspicion spawns Keepers")
game.pending_toasts.clear()
pe._use_rift()
expect(game.flags["escaped_keepers"], "fleeing with Keepers sets the escape flag")
expect("panic" in game.flags["achievements"], "escaping the Keepers unlocks Total Panic")
expect(any(a["id"] == "panic" for a in game.pending_toasts),
       "the escape queues a toast for the hub")
settle()
expect(isinstance(game.scene, TroiScene), "escape -> troi")

expect("escape_troi" not in game.flags["achievements"], "the Troi-escape is unobtainable")
game.flags.sync_achievements()
expect("escape_troi" not in game.flags["achievements"],
       "the Troi-escape stays unobtainable even after a sync")

tm = TerminalModal({"host": "x@troi", "win_cmds": ["post a.txt"],
                    "files": {"a.txt": ["hi"]}, "win": ["ok"]})
term_type(tm, "help")
term_key(tm, pygame.K_RETURN)
term_type(tm, "post a.txt")
term_key(tm, pygame.K_RETURN)
for _ in range(60):
    tm.update(50)
expect(tm.done == "success", "terminal win command completes the task")

tr = TrainingScene(game)
game.scene = tr
tr.on_enter()
for _ in range(6):
    tr.update(50)
    tr.draw(game.screen)
    key(pygame.K_RETURN)
expect(isinstance(game.scene, TrainingScene), "training scene runs")

game.flags["visits"] = 0
first = " ".join(d["text"] for d in content.boss_return(game.flags))
expect("Troi" not in first, "post-tutorial return never mentions the Troi")
game.flags["visits"] = 4
backs = {" ".join(d["text"] for d in content.boss_return(game.flags)) for _ in range(40)}
expect(len(backs) > 1, "returned-from-mission boss line varies")

game.flags.new_life()
game.flags["run_seed"] = 777
te = EraScene(game)
te.on_enter(key="1998")
game.scene = te
tk = next((o for o in te.objects if o.take), None)
expect(tk is not None, "era has takeable objects")
before = te.suspicion
te._take(tk)
expect(tk.take in game.flags["satchel"], "taking adds the item to the satchel")
expect(game.flags["instability"] == 1, "taking raises instability")
expect(te.suspicion > before, "taking spikes attention")
te2 = EraScene(game)
te2.on_enter(key="2001")
expect(te2.suspicion > 0, "carrying contraband starts the next era already watched")

import sound
sound.music("hub")
sound.sfx("rift")
sound.footsteps(True)
sound.footsteps(False)
muted = sound.toggle()
sound.toggle()
expect(muted is False, "audio system runs without files (graceful no-op)")

if os.path.exists("save.test.json"):
    os.remove("save.test.json")
failed = [m for ok, m in checks if not ok]
print("\n%d/%d checks passed" % (len(checks) - len(failed), len(checks)))
if failed:
    raise SystemExit("FAILURES:\n  " + "\n  ".join(failed))
print("SMOKE TEST PASSED")
