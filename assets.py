"""Cached image loading. Call only after the display has been created."""

import pygame

_cache = {}


def image(path, size=None):
    key = (path, size)
    img = _cache.get(key)
    if img is None:
        img = pygame.image.load(path).convert_alpha()
        if size is not None:
            img = pygame.transform.scale(img, size)
        _cache[key] = img
    return img


def fit(path, max_w, max_h):
    """Scale an image to fit within (max_w, max_h) preserving aspect ratio —
    so a tall sprite (the boss) isn't squashed into a square frame."""
    key = ("fit", path, max_w, max_h)
    img = _cache.get(key)
    if img is None:
        src = pygame.image.load(path).convert_alpha()
        w, h = src.get_size()
        scale = min(max_w / w, max_h / h)
        img = pygame.transform.scale(src, (max(1, round(w * scale)), max(1, round(h * scale))))
        _cache[key] = img
    return img


def tinted(path, size, color, alpha=255):
    """Return a silhouette of an image filled with *color* (for ghosts)."""
    key = (path, size, color, alpha)
    img = _cache.get(key)
    if img is None:
        base = image(path, size).copy()
        overlay = pygame.Surface(base.get_size(), pygame.SRCALPHA)
        overlay.fill((*color, 255))
        base.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        base.set_alpha(alpha)
        _cache[key] = base
        img = base
    return img
