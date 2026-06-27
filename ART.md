# Pixel art spec — Time Traveller's Dilemma

Drop a PNG in the right place and it **auto-replaces** the procedural shape —
no code changes. Anything you haven't drawn keeps using the placeholder art,
so you can do this one sprite at a time.

**General rules**
- PNG with transparency (RGBA).
- Draw at the exact pixel size listed (or any image at that aspect ratio — the
  game scales it to the footprint). Exact size = no scaling = crispest.
- Top-down or slight 3/4 view. The **bottom edge** of the image is the sprite's
  "feet" (the game sorts depth by bottom edge), so stand things on the bottom.
- Keep a consistent light direction (top-left is fine).

---

## 1. Characters  (replace these files directly in `textures/`)

| File | Size | Notes |
|---|---|---|
| `player_down_1.png`, `player_down_2.png` | 32×32 | 2-frame walk, facing down |
| `player_up_1.png`, `player_up_2.png` | 32×32 | facing up |
| `player_left_1.png`, `player_left_2.png` | 32×32 | facing left |
| `player_right_1.png`, `player_right_2.png` | 32×32 | facing right |
| `npc1.png` | 32×32 | also tinted/ghosted for Troi floaters & "the boy"/clerk |
| `npc2.png` | 32×32 | also used for Time Keepers (tinted amber) |
| `npc3.png` | 32×32 | astronomer / patron / the figure |
| `boss.png` | 128×256 | tall figure; used as dialogue portrait and looming in the hub |

(These are square so they read at any facing. The 8 player frames are the
single biggest visual upgrade — start here.)

---

## 2. Props  (new files in `textures/props/`)

Filename = `<kind>.png` at the size below. Optional per-era variant:
`<theme>_<kind>.png` (themes: `cafe`, `garage`, `observatory`, `ruin`, `cave`)
— e.g. `cafe_table.png` only changes tables in 2001.

**Highest impact (used as scenery across eras):**

| kind | size | appears in |
|---|---|---|
| `table` | 74×52 | cafe, observatory |
| `chair` | 40×28 | cafe |
| `crt` | 80×84 | cafe (also the 2001 terminal) |
| `server` | 70×110 | cafe, ruin |
| `shelf` | 90×80 | cafe, garage, observatory |
| `plant` | 46×60 | cafe, garage |
| `crate` | 70×70 | garage, ruin, cave |
| `barrel` | 50×64 | garage, ruin |
| `cot` | 120×60 | garage |
| `tree` | 60×70 | garage |
| `pillar` | 50×130 | observatory, ruin |
| `candle` | 44×70 | observatory (altar) |
| `bookshelf` | 90×90 | observatory |
| `telescope` | 90×90 | observatory |
| `rubble` | 80×50 | ruin, cave |
| `monument` | 70×150 | ruin |
| `stalagmite` | 50×100 | cave |

**Quest objects (the things you interact with):**

| kind | size | what it is |
|---|---|---|
| `poster` | 70×84 | notice board / photos / ledger |
| `payphone` | 60×90 | 2001 payphone |
| `computer` | 90×70 | the IBM 5100 |
| `desk` | 110×60 | workbench / manuscript desk |
| `core` | 80×100 | the Keeper Core (3744) |
| `console` | 90×80 | spire console |
| `fire` | 72×72 | the cave fire |
| `painting` | 120×90 | the painted cave wall (the spiral) |

**Skip for now:** `wall` (drawn at many sizes — needs a tileable texture; we'll
wire that separately), `rug`, `counter`.

---

## 3. Optional later
- **Floor tiles** per theme (`textures/floors/<theme>.png`, ~72×72 tileable) —
  tell me and I'll wire `bake_floor` to use them.
- **Animated props** (fire/candle/crt currently shimmer procedurally) — a static
  sprite is fine; multi-frame support can be added if you want them to flicker.

---

## Suggested order
1. The 8 **player** frames + **boss.png** + **npc1-3** → instantly lifts every scene.
2. The 2001 set (`crt`, `table`, `chair`, `server`, `shelf`, `plant`, `poster`,
   `payphone`, `computer`) → makes one era look finished end-to-end.
3. Roll out the rest by era.

Drop files in and run `python main.py` — they appear immediately.
