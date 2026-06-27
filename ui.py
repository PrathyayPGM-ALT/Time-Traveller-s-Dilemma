"""Small shared UI helpers for a consistent, polished look."""

import math

import pygame

import config


def wavy_text(screen, font, s, color, x, y, center=False, alpha=255,
              amp=3.0, speed=11.0):
    """Render text with a per-character vertical wave (Undertale-style shake)
    for aggressive lines. Assumes a monospace font (IBM Plex Mono)."""
    cw = font.size("M")[0]
    if center:
        x -= (cw * len(s)) // 2
    t = pygame.time.get_ticks() / 1000.0
    for i, ch in enumerate(s):
        if ch == " ":
            continue
        dy = math.sin(t * speed + i * 0.55) * amp
        sh = font.render(ch, True, (0, 0, 0))
        sh.set_alpha(min(alpha, 150))
        screen.blit(sh, (x + i * cw + 2, y + dy + 2))
        g = font.render(ch, True, color)
        if alpha < 255:
            g.set_alpha(alpha)
        screen.blit(g, (x + i * cw, y + dy))


def text(screen, font, s, color, x, y, center=False, right=False,
         shadow=True, alpha=255):
    surf = font.render(s, True, color)
    if alpha < 255:
        surf.set_alpha(alpha)
    if center:
        x -= surf.get_width() // 2
    elif right:
        x -= surf.get_width()
    if shadow:
        sh = font.render(s, True, (0, 0, 0))
        sh.set_alpha(min(alpha, 160))
        screen.blit(sh, (x + 2, y + 2))
    screen.blit(surf, (x, y))
    return surf.get_width()


def panel(screen, rect, fill=(16, 16, 20, 230), border=(64, 64, 76),
          accent=None, radius=10, width=2):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(s, fill, s.get_rect(), border_radius=radius)
    screen.blit(s, rect.topleft)
    if accent:
        cap = pygame.Surface((rect.w, 4), pygame.SRCALPHA)
        cap.fill((*accent, 255))
        screen.blit(cap, (rect.x, rect.y + 1))
    pygame.draw.rect(screen, border, rect, width, border_radius=radius)


def chip(screen, font, s, color, x, y):
    w = font.size(s)[0]
    rect = pygame.Rect(x, y, w + 18, 24)
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, 36), surf.get_rect(), border_radius=12)
    pygame.draw.rect(surf, (*color, 150), surf.get_rect(), 1, border_radius=12)
    screen.blit(surf, rect.topleft)
    text(screen, font, s, color, x + 9, y + 3, shadow=False)
    return rect.w


def bar(screen, rect, frac, fill, back=(36, 34, 26), border=(90, 76, 36)):
    pygame.draw.rect(screen, back, rect, border_radius=3)
    inner = pygame.Rect(rect.x, rect.y, int(rect.w * max(0, min(1, frac))), rect.h)
    pygame.draw.rect(screen, fill, inner, border_radius=3)
    pygame.draw.rect(screen, border, rect, 1, border_radius=3)
    # tick marks
    for i in range(1, 5):
        x = rect.x + rect.w * i // 5
        pygame.draw.line(screen, (0, 0, 0), (x, rect.y), (x, rect.bottom), 1)


def scrim(screen, rect, alpha=120):
    s = pygame.Surface(rect.size, pygame.SRCALPHA)
    s.fill((0, 0, 0, alpha))
    screen.blit(s, rect.topleft)


def achievement_toast(screen, achievements, t, top=70):
    """Draw an 'ACHIEVEMENT UNLOCKED' banner that fades in, holds, fades out.

    `achievements` is a list of achievement dicts; `t` is seconds since the
    toast started. Does nothing once the toast has run its ~6s course.
    """
    if not achievements or t > 6.0:
        return
    if t < 0.4:
        alpha = int(t / 0.4 * 255)
    elif t > 5.0:
        alpha = int((6.0 - t) * 255)
    else:
        alpha = 255
    alpha = max(0, min(255, alpha))

    n = len(achievements)
    pw, rh = 360, 50
    ph = 30 + rh * n
    px = config.WIDTH // 2 - pw // 2
    surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
    surf.fill((10, 8, 12, int(alpha * 0.86)))
    pygame.draw.rect(surf, (*config.TITOR, alpha), surf.get_rect(), 2)
    screen.blit(surf, (px, top))

    text(screen, config.font(15), "ACHIEVEMENT UNLOCKED", config.TITOR,
         config.WIDTH // 2, top + 8, center=True, alpha=alpha, shadow=False)
    for i, a in enumerate(achievements):
        ry = top + 30 + i * rh
        text(screen, config.font(20), a["name"], config.WHITE,
             config.WIDTH // 2, ry, center=True, alpha=alpha)
        text(screen, config.font(13), a["desc"], config.DIM,
             config.WIDTH // 2, ry + 24, center=True, alpha=alpha, shadow=False)
