# Time Traveller's Dilemma

A short, atmospheric time-travel game with a psychological-horror streak, built
in Python with [pygame-ce](https://pyga.me/).

The year is **4200**. You wake in a borrowed body you don't remember stepping
into, and a voice that has never shown its face calls you **Prisoner 7**. It
gives you a machine and sends you back through five eras — **2001, 1998, 1683,
3744, and 24567 BC** — each a place you have to *think* your way out of before
the year notices you. Every jump passes through the **Troi**. You think this is
your first life. It isn't.

## Run from source

Requires Python 3.11+ and pygame-ce.

```bash
pip install pygame-ce
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| E | Interact · read · talk |
| T | Take an item |
| Enter / Space | Advance text |
| M | Mute |
| Esc | Back / give up |

## Builds

- **Windows .exe** (PyInstaller, one file): `python build.py` → `dist/`
- **Web / browser** (pygbag → WebAssembly): `python build_web.py` → `web_build/build/web/`

## Tests

A headless smoke test drives every scene and the core mechanics:

```bash
python test_smoke.py
```

## Project layout

- `main.py` — entry point and scene wiring
- `scene.py` — game loop, scene manager, persistent save ("soul") state
- `flow.py` / `hub.py` / `troi.py` / `era.py` / `training.py` — the scenes
- `worldgen.py` / `world.py` — procedural era layouts and props
- `content.py` — all narrative content, puzzles, and achievements
- `dialogue.py` / `ui.py` / `narrator.py` / `codelock.py` / `terminal.py` — UI
- `make_art.py` — procedural pixel-art generator (dev tool)
- `textures/`, `fonts/`, `sounds/` — assets

## Notes on assets / licensing

The font is IBM Plex Mono (SIL Open Font License). Audio in `sounds/` was
contributed for this project. If you fork or redistribute, check you have the
right to reuse any bundled audio, and consider adding a `LICENSE` file for your
own terms.
