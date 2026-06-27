# Character pixel maps (16×16)

> These are now generated (with shading) by **`make_art.py`** — that file is the
> live source of truth (`PLAYER_DOWN_1` … `PLAYER_SIDE_2`, `npc_grid`). This doc
> mirrors the palettes + a couple of grids; edit the grids in make_art.py and
> run `python make_art.py` to rebuild. To hand-paint instead, just overwrite the
> PNGs in `textures/`.

Read each grid like a map: 16 rows × 16 columns, one character = one pixel.
The letter = a colour from the legend. `.` = transparent. Row 0 = top, col 0 = left.
Files go in `textures/` (PNG, transparent). Light source is **top-left**.

---

# PLAYER — "Prisoner 7"  (gaunt, hollow-eyed, a flicker of self in the glint)

## Palette
Coat is shaded: `L` = base lightened (+26/channel), `R` = base, `r` = darkened
(−22). To recolour the coat, change only `R`.

| Key | Hex | RGB | What |
|-----|-----|-----|------|
| `.` | — | — | transparent |
| `D` | `#100E12` | 16,14,18 | outline |
| `H` | `#34303A` | 52,48,58 | hair |
| `h` | `#201E28` | 32,30,40 | hair shadow (right falloff) |
| `S` | `#C0B4AC` | 192,180,172 | skin (ashen) |
| `s` | `#968884` | 150,136,132 | skin shadow / gaunt cheek |
| `E` | `#121016` | 18,16,22 | hollow eye socket |
| `e` | `#9AA8B0` | 154,168,176 | eye glint (cold) |
| `m` | `#4A2E30` | 74,46,48 | mouth |
| `L` | `#8E5250` | 142,82,80 | coat lit (left edge) |
| `R` | `#743836` | 116,56,54 | coat base |
| `r` | `#5E2220` | 94,34,32 | coat shadow (right edge) |
| `P` | `#323440` | 50,52,64 | trousers |
| `p` | `#242632` | 36,38,50 | trouser shadow |
| `K` | `#1C1A22` | 28,26,34 | boots |

## player_down_1  (facing camera — idle / contact frame)
```
................
....DHHHHD......
...DHHHHHhD.....
...DHSSSShD.....
...DEesseED.....
...DsSssSsD.....
...DSsmmsSD.....
....DSSSD.......
...DLRRRRrD.....
..DLRRRRRRrD....
..DSRRRRRRSD....
...DLRRRRrD.....
...DLRRRRrD.....
...DpPPPpD......
...DKD.DKD......
...DK...KD......
```

**The other 7 frames** (down_2, up_1/2, right_1/2; **left = mirror of right**)
live in `make_art.py` as `PLAYER_DOWN_2` … `PLAYER_SIDE_2`. They reuse the head
above; the walk frame swaps the feet rows, `up` shows hair instead of a face,
and `right` is a profile with one eye. Both `left` files must still exist on
disk (just the mirrored right).

---

# NPCs — "familiar but wrong"  (vacant, dead-eyed, no mouth)

All three share the SAME pixel map; only the hair (`H`), coat (`C`) and coat
shadow (`c`) colours change. Front-facing, single frame.

## Shared palette
Coat shaded the same way: `L` = lit / `C` = base / `c` = shadow.

| Key | Hex | RGB | What |
|-----|-----|-----|------|
| `.` | — | — | transparent |
| `D` | `#121016` | 18,16,22 | outline |
| `S` | `#B6ACA6` | 182,172,166 | skin |
| `s` | `#8C8280` | 140,130,128 | skin shadow |
| `E` | `#0E0C12` | 14,12,18 | dead eye (no glint) |
| `K` | `#201E26` | 32,30,38 | boots |
| `H` / `C` / `c` / `L` | per NPC | — | hair / coat / coat-shadow / coat-lit |

## Per-NPC base colours  (`C`; `L`=+26, `c`=−22 auto)
| NPC | role | `H` hair | `C` coat (base) |
|-----|------|----------|-----------------|
| `npc1` | familiar (boy / clerk) | `#28262C` 40,38,44 | `#424E68` 66,78,104 dull slate |
| `npc2` | watcher (keeper-tinted) | `#22201E` 34,32,30 | `#5C5848` 92,88,72 drab olive |
| `npc3` | the knowing double | `#2E2A28` 46,42,40 | `#46605C` 70,96,92 faded teal |

## npc grid  (long spectral coat; dead eyes; no mouth)
```
................
....DHHHHD......
...DHHHHHhD.....
...DHSSSShD.....
...DSEEEESD.....
...DsSssSsD.....
...DSssssSD.....
....DSSSD.......
...DLCCCcD......
..DLCCCCCcD.....
..DSCCCCCSD.....
...DLCCCcD......
...DLCCCcD......
...DLCCCcD......
...DKD.DKD......
................
```

---

## The one rule that sells the horror
- **Player eyes** = hollow `E` with one `e` glint each: `D E e s s e E D`.
- **NPC eyes** = solid `E E E E` band — **no glint, no mouth.**

That single glint is the only thing saying the player is still *someone*. Keep
the NPCs blank.
