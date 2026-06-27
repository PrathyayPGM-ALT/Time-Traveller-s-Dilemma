# sounds/

Drop audio files here and the game plays them automatically. Anything missing
is silently skipped, so you can add them one at a time.

- **Formats:** `.ogg` (best for music), `.mp3`, or `.wav`. Name = exactly as
  below + the extension (e.g. `hub.ogg`, `footsteps.mp3`).
- **Music** is streamed and **looped**, so make each bed loop cleanly.
- Press **M** in game to mute everything.

## Always-on
| file | when it plays |
|------|----------------|
| `ambience` | a persistent creepy bed — loops under **every** scene, the whole game |
| `footsteps` | loops while the player is walking (eras, the Troi, training) |

## Music beds (looping, one per scene)
| file | scene / mood |
|------|--------------|
| `title` | title screen |
| `hub` | the 4200 hub + the opening cutscene (the boss) |
| `troi` | the Troi (the void between jumps) |
| `trapped` | caught by the Keepers — trapped forever |
| `ending` | the loop closes |
| `era_cafe` | 2001 — internet café |
| `era_garage` | 1998 — suburban home |
| `era_observatory` | 1683 — observatory |
| `era_ruin` | 3744 — dead city |
| `era_cave` | 24567 BC — cave |

## One-shot SFX
| file | trigger |
|------|---------|
| `interact` | pressing E on something |
| `rift` | stepping through a rift / time-travelling |
| `keeper` | the Time Keepers wake up |
| `take` | stealing an item (the satchel / instability) |

Wiring lives in `sound.py`; tweak volumes there (`MUSIC_VOL`, `SFX_VOL`,
`FOOT_VOL`).
