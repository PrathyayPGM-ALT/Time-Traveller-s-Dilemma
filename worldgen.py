"""Procedural era layout generation.

The *story* of an era (quests, dialogue, theme, props) is authored in
content.py. The *space* — rooms, walls, doors, where everything sits — is
generated here, seeded per life so each new game's world is genuinely new
while staying stable within a single playthrough.
"""

import random

import pygame

WALL = 22
DOOR = 140
NPC_SIZE = 44
PLAYER_SIZE = 48

# Default footprint per prop kind.
PROP_SIZE = {
    "crt": (80, 84), "computer": (90, 70), "poster": (70, 84), "payphone": (60, 90),
    "desk": (110, 60), "candle": (44, 70), "core": (80, 100), "console": (90, 80),
    "monument": (70, 150), "crate": (70, 70), "barrel": (50, 64), "fire": (72, 72),
    "painting": (120, 90), "table": (74, 52), "chair": (40, 28), "plant": (46, 60),
    "shelf": (90, 80), "bookshelf": (90, 90), "server": (70, 110), "pillar": (50, 130),
    "rubble": (80, 50), "telescope": (90, 90), "cot": (120, 60), "tree": (60, 70),
    "stalagmite": (50, 100), "counter": (200, 42), "rug": (160, 110),
}
NON_SOLID = {"rug", "poster", "painting"}


def _size(prop):
    return PROP_SIZE.get(prop, (70, 70))


def _vwall(x, y0, y1, gaps):
    segs, cur = [], y0
    for gy, gh in sorted(gaps):
        if gy > cur:
            segs.append((x, cur, WALL, gy - cur))
        cur = max(cur, gy + gh)
    if cur < y1:
        segs.append((x, cur, WALL, y1 - cur))
    return segs


def _hwall(y, x0, x1, gaps):
    segs, cur = [], x0
    for gx, gw in sorted(gaps):
        if gx > cur:
            segs.append((cur, y, gx - cur, WALL))
        cur = max(cur, gx + gw)
    if cur < x1:
        segs.append((cur, y, x1 - cur, WALL))
    return segs


def _place(room, w, h, placed, rng, inset=84, spacing=46, tries=80):
    if room.w - 2 * inset - w < 1 or room.h - 2 * inset - h < 1:
        inset = 40
    for _ in range(tries):
        x = rng.randint(room.x + inset, max(room.x + inset, room.right - inset - w))
        y = rng.randint(room.y + inset, max(room.y + inset, room.bottom - inset - h))
        r = pygame.Rect(x, y, w, h)
        if not any(r.inflate(spacing, spacing).colliderect(p) for p in placed):
            placed.append(r)
            return r
    r = pygame.Rect(room.centerx - w // 2, room.centery - h // 2, w, h)
    placed.append(r)
    return r


def build(spec, seed):
    rng = random.Random(seed)

    cols, rows = rng.choice([(2, 2), (3, 2), (2, 3), (3, 2), (3, 3)])
    rw = rng.randint(560, 680)
    rh = rng.randint(470, 560)
    M = 50

    world_w = M * 2 + WALL + cols * (rw + WALL)
    world_h = M * 2 + WALL + rows * (rh + WALL)

    def room_rect(c, r):
        return pygame.Rect(M + WALL + c * (rw + WALL),
                           M + WALL + r * (rh + WALL), rw, rh)

    rooms = [(c, r, room_rect(c, r)) for r in range(rows) for c in range(cols)]

    # --- walls with doors ------------------------------------------------
    x0, x1 = M, world_w - M
    y0, y1 = M, world_h - M
    walls = []

    # vertical wall lines (i = 0..cols)
    for i in range(cols + 1):
        x = M + i * (rw + WALL)
        gaps = []
        if 0 < i < cols:  # interior line -> a door per row
            for r in range(rows):
                ry = M + WALL + r * (rh + WALL)
                gy = ry + rng.randint(60, max(60, rh - DOOR - 60))
                gaps.append((gy, DOOR))
        walls += _vwall(x, y0, y1, gaps)

    # horizontal wall lines (j = 0..rows)
    for j in range(rows + 1):
        y = M + j * (rh + WALL)
        gaps = []
        if 0 < j < rows:
            for c in range(cols):
                rx = M + WALL + c * (rw + WALL)
                gx = rx + rng.randint(60, max(60, rw - DOOR - 60))
                gaps.append((gx, DOOR))
        walls += _hwall(y, x0, x1, gaps)

    # --- choose spawn + rift rooms --------------------------------------
    bottom = [t for t in rooms if t[1] == rows - 1]
    top = [t for t in rooms if t[1] == 0]
    spawn_room = rng.choice(bottom)
    rift_room = rng.choice([t for t in top if t != spawn_room] or top)

    placed = {id(t[2]): [] for t in rooms}

    # Reserve a clear, player-sized area and spawn at its centre (not offset
    # below it — that used to drop the player straight into a prop).
    spawn_rect = _place(spawn_room[2], PLAYER_SIZE + 20, PLAYER_SIZE + 20,
                        placed[id(spawn_room[2])], rng, inset=100, spacing=72)
    spawn = (spawn_rect.centerx - PLAYER_SIZE // 2,
             spawn_rect.centery - PLAYER_SIZE // 2)

    # --- assign clues + the lock to rooms -------------------------------
    objs = list(spec.get("objects", []))
    npcs = list(spec.get("npcs", []))
    by_id = {o["id"]: ("obj", o) for o in objs}
    by_id.update({n["id"]: ("npc", n) for n in npcs})
    lock_id = spec.get("puzzle", {}).get("lock")

    # spread everything across rooms (round-robin), preferring non-spawn rooms
    # first so clues force exploration; the lock is pushed away from spawn.
    other_rooms = [t for t in rooms if t != spawn_room]
    rng.shuffle(other_rooms)
    order = [t[2] for t in (other_rooms + [spawn_room])]
    room_for = {}
    for i, oid in enumerate(by_id):
        room_for[oid] = order[i % len(order)]
    if lock_id and room_for.get(lock_id) is spawn_room[2] and other_rooms:
        room_for[lock_id] = order[0]

    out_objs, out_npcs = [], []
    for oid, room in room_for.items():
        kind, data = by_id[oid]
        if kind == "obj":
            w, h = _size(data.get("prop", "console"))
            r = _place(room, w, h, placed[id(room)], rng)
            out_objs.append(dict(data, x=r.x, y=r.y, w=w, h=h,
                                 solid=data.get("solid", data.get("prop") not in NON_SOLID)))
        else:
            r = _place(room, NPC_SIZE, NPC_SIZE, placed[id(room)], rng)
            out_npcs.append(dict(data, x=r.x, y=r.y,
                                 radius=min(data.get("radius", 80),
                                            min(room.w, room.h) // 2 - 60)))

    # the rift (always present, in the rift room)
    rw_, rh_ = _size("rug")
    rr = _place(rift_room[2], rw_, rh_, placed[id(rift_room[2])], rng)
    out_objs.append({"id": "rift", "label": "RIFT", "kind": "exit", "prop": "rug",
                     "lines": [], "solid": False,
                     "x": rr.x, "y": rr.y, "w": rw_, "h": rh_})

    # --- scatter decor ---------------------------------------------------
    decor = []
    kinds = spec.get("decor_kinds", ["crate"])
    for (_, _, room) in rooms:
        for _ in range(rng.randint(3, 7)):
            kind = rng.choice(kinds)
            w, h = _size(kind)
            r = _place(room, w, h, placed[id(room)], rng, inset=70, spacing=28, tries=40)
            decor.append({"kind": kind, "x": r.x, "y": r.y, "w": w, "h": h,
                          "solid": kind not in NON_SOLID})

    # --- spawn safety net: never start the player inside a solid ---------
    solids = [pygame.Rect(*w) for w in walls]
    solids += [pygame.Rect(d["x"], d["y"], d["w"], d["h"])
               for d in decor if d.get("solid", True)]
    solids += [pygame.Rect(o["x"], o["y"], o["w"], o["h"]) for o in out_objs
               if o.get("solid", True) and o.get("kind") != "exit"]
    sr = spawn_room[2]

    def clear(x, y):
        pr = pygame.Rect(int(x), int(y), PLAYER_SIZE, PLAYER_SIZE)
        return not any(pr.colliderect(s) for s in solids)

    if not clear(*spawn):
        for _ in range(300):
            x = rng.randint(sr.x + 90, max(sr.x + 90, sr.right - 90 - PLAYER_SIZE))
            y = rng.randint(sr.y + 90, max(sr.y + 90, sr.bottom - 90 - PLAYER_SIZE))
            if clear(x, y):
                spawn = (x, y)
                break

    # --- zones (named rooms) --------------------------------------------
    names = list(spec.get("zone_names", []))
    rng.shuffle(names)
    zones = []
    for k, (_, _, room) in enumerate(rooms):
        nm = names[k] if k < len(names) else "An Unremembered Place"
        zones.append({"rect": (room.x, room.y, room.w, room.h), "name": nm})

    return {
        "world": (world_w, world_h),
        "spawn": spawn,
        "walls": walls,
        "decor": decor,
        "objects": out_objs,
        "npcs": out_npcs,
        "zones": zones,
    }
