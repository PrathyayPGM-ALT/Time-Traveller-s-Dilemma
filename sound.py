"""Music + SFX + footstep playback.

All audio lives in the `sounds/` folder as `<name>.ogg`/`.mp3`/`.wav`. Drop
files in and they play; anything missing is a graceful no-op. Press M to mute.

Expected names (see sounds/README.md):
  music beds (loop): title, hub, troi, trapped, ending,
                     era_cafe, era_garage, era_observatory, era_ruin, era_cave
  one-shot SFX:      interact, rift, keeper, take
  footsteps:         footsteps   (looped while the player walks)
"""

import os
import sys

import pygame

IS_WEB = sys.platform == "emscripten"

SOUND_DIR = "sounds"
EXTS = (".ogg", ".mp3", ".wav")
MUSIC_VOL = 0.7
SFX_VOL = 0.7
FOOT_VOL = 0.5
AMB_VOL = 0.6

ENABLED = True
_ready = False
_cur = None
_sfx = {}
_foot = None
_foot_loaded = False
_foot_chan = None
_foot_on = False
_amb = None
_amb_loaded = False
_amb_chan = None


def init():
    global _ready, _foot_chan, _amb_chan
    if IS_WEB:
        _ready = False
        return
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        _foot_chan = pygame.mixer.Channel(15)
        _amb_chan = pygame.mixer.Channel(14)
        _ready = True
    except Exception:
        _ready = False


def _find(name):
    for ext in EXTS:
        path = os.path.join(SOUND_DIR, name + ext)
        if os.path.exists(path):
            return path
    return None


def _vol():
    return MUSIC_VOL if ENABLED else 0.0


def music(name, fade=900):
    global _cur
    if not _ready or name == _cur:
        return
    path = _find(name)
    if not path:
        try:
            pygame.mixer.music.fadeout(fade)
        except pygame.error:
            pass
        _cur = None
        return
    _cur = name
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(_vol())
        pygame.mixer.music.play(-1, fade_ms=fade)
    except pygame.error:
        _cur = None


def ambience():
    """Start the persistent creepy bed (sounds/ambience.*), looped forever and
    layered under every scene. Safe to call repeatedly."""
    global _amb, _amb_loaded
    if not _ready:
        return
    if not _amb_loaded:
        _amb_loaded = True
        path = _find("ambience")
        if path:
            try:
                _amb = pygame.mixer.Sound(path)
            except pygame.error:
                _amb = None
    if _amb and _amb_chan and not _amb_chan.get_busy():
        _amb.set_volume(AMB_VOL if ENABLED else 0.0)
        _amb_chan.play(_amb, loops=-1, fade_ms=1500)


def stop_music(fade=600):
    global _cur
    if _ready:
        try:
            pygame.mixer.music.fadeout(fade)
        except pygame.error:
            pass
    _cur = None


def sfx(name):
    if not (_ready and ENABLED):
        return
    s = _sfx.get(name, "?")
    if s == "?":
        path = _find(name)
        s = None
        if path:
            try:
                s = pygame.mixer.Sound(path)
            except pygame.error:
                s = None
        _sfx[name] = s
    if s:
        s.set_volume(SFX_VOL)
        s.play()


def footsteps(moving):
    global _foot, _foot_loaded, _foot_on
    if not (_ready and ENABLED):
        return
    if not _foot_loaded:
        _foot_loaded = True
        path = _find("footsteps")
        if path:
            try:
                _foot = pygame.mixer.Sound(path)
            except pygame.error:
                _foot = None
    if _foot is None or _foot_chan is None:
        return
    if moving and not _foot_on:
        _foot.set_volume(FOOT_VOL)
        _foot_chan.play(_foot, loops=-1, fade_ms=60)
        _foot_on = True
    elif not moving and _foot_on:
        _foot_chan.fadeout(110)
        _foot_on = False


def stop_footsteps():
    global _foot_on
    if _ready and _foot_chan and _foot_on:
        _foot_chan.fadeout(80)
        _foot_on = False


def toggle():
    global ENABLED
    ENABLED = not ENABLED
    if _ready:
        try:
            pygame.mixer.music.set_volume(_vol())
            if _amb_chan:
                _amb_chan.set_volume(AMB_VOL if ENABLED else 0.0)
        except pygame.error:
            pass
        if not ENABLED:
            stop_footsteps()
    return ENABLED
