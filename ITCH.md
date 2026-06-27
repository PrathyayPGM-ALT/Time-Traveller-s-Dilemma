# Time Traveller's Dilemma

### Short description (itch "summary" field)
A criminal in the ruins of 4200 is sent back through five thousand years by a boss who's never shown his face. Every jump passes through the Troi. You think this is your first life. It isn't.

---

## Full description (page body)

The year is **4200**. The sky is the colour of rust and old smoke, the earth is a
spoil, and you wake in a borrowed body you don't remember stepping into. A voice
that has never shown its face calls you **Prisoner 7** — and seems to know you far
better than you know yourself.

The boss gives you the machine. You travel. And every time you fall through the
years you pass through the **Troi** — a grey seam between places where familiar
figures drift, half-remembered, mouthing things you're certain you've heard before.

What you do in the past is not a rescue. It may be the cause.

---

**Time Traveller's Dilemma** is a short, atmospheric time-travel game with a
psychological-horror streak. Five eras — **2001, 1998, 1683, 3744, and 24567 BC** —
each a place you explore and have to *think* your way out of. No quest arrows, no
"press here." Read the room. Find the clues. Work out the answer yourself.

### Features
- **Five eras, five puzzles.** Each one is a self-contained mystery: gather clues,
  crack the lock, get out — before the year notices you.
- **No hand-holding.** A single cryptic directive and a world that won't explain
  itself. Deduce the rest.
- **Worlds that rearrange.** Every life lays the eras out anew.
- **A story that remembers.** Click "new journey" and… you'll see.
- **The Time Keepers.** Linger, steal, or stray off-task and they wake. If they
  catch you, there is no game-over screen — only the Troi, forever.
- **Take what isn't yours.** Carry an artefact between centuries — but everything
  you pocket tears a hole behind you, and the Keepers feel it.
- **A boss you'll learn to hate**, who runs your orientation personally and is not
  enjoying it.

### Controls
| Key | Action |
|-----|--------|
| WASD / Arrows | Move |
| E | Interact · read · talk |
| T | Take an item |
| Enter / Space | Advance text |
| M | Mute |
| Esc | Back / give up |

### How to play
**Play right here in your browser** — hit *Run*, give it a moment to load, and
you're in. Prefer to play offline? **Download the Windows build**, double-click
**TimeTravellersDilemma.exe**, and go. No install, no Python — everything's
bundled, and your progress saves beside the game.

*A loop with a question at the bottom of it. Try not to recognise anyone.*

> Content note: themes of memory loss, war, and quiet existential dread. No gore.

---

**Suggested itch tags:** time-travel, psychological-horror, puzzle, exploration,
narrative, pixel-art, atmospheric, singleplayer, mystery, short

---

## Publishing to itch.io (dev notes — not page text)

You ship **two** things on the same itch page: a browser version and a download.

**1. Web (playable in browser)**
- Build: `python build_web.py`  → output in `web_build/build/web/`
- Zip the **contents** of that folder (so `index.html` sits at the zip root —
  don't zip the folder itself).
- itch → *Upload files* → add the zip → tick **"This file will be played in the
  browser"**.
- Set the embed size to **1000 × 800** (or check *fullscreen*).
- **Leave "SharedArrayBuffer support" OFF.** This build is single-threaded and
  doesn't need it — and turning it on enables cross-origin isolation, which on
  some browsers blocks pygbag from downloading its runtime from the CDN and
  makes the game hang forever on a grey screen. Only enable it if a build
  actually requires threads (this one doesn't).

**2. Windows download (offline)**
- Build: `python build.py`  → `dist/TimeTravellersDilemma.exe`
- Upload the `.exe` and tick **"This file will be downloaded"** + platform
  **Windows**.

The web build uses `.ogg` audio (browsers/pygbag can't play `.mp3`); the desktop
build happily uses either. Both share one `save.json`-style "soul" *per machine*
— note the in-browser save persists only for that browser/session, so the full
"new journey isn't new" effect is most reliable in the download.
