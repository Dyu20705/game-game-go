"""Reusable icon drawing helpers."""

import pygame


def make_icon_surface(kind, size, bg_color=(86, 113, 136), fg_color=(255, 255, 255)):
    """Create a circular icon surface for common UI actions."""
    width, height = size
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    center = (width // 2, height // 2)
    radius = max(8, min(width, height) // 2 - 2)

    pygame.draw.circle(surface, bg_color, center, radius)
    pygame.draw.circle(surface, (255, 255, 255, 210), center, radius, 2)

    if kind == "back":
        _draw_back_glyph(surface, center, radius, fg_color)
    elif kind == "settings":
        _draw_settings_glyph(surface, center, radius, fg_color)
    elif kind == "restart":
        _draw_restart_glyph(surface, center, radius, fg_color)
    elif kind == "home":
        _draw_home_glyph(surface, center, radius, fg_color)
    elif kind == "tutorial":
        _draw_tutorial_glyph(surface, center, radius, fg_color)

    return surface


def _draw_back_glyph(surface, center, radius, color):
    cx, cy = center
    shaft_w = max(10, int(radius * 0.95))
    shaft_h = max(3, int(radius * 0.22))
    shaft_rect = pygame.Rect(cx - shaft_w // 4, cy - shaft_h // 2, shaft_w, shaft_h)
    pygame.draw.rect(surface, color, shaft_rect, border_radius=2)

    tip = [
        (cx - shaft_w // 2, cy),
        (cx - shaft_w // 6, cy - max(6, int(radius * 0.45))),
        (cx - shaft_w // 6, cy + max(6, int(radius * 0.45))),
    ]
    pygame.draw.polygon(surface, color, tip)


def _draw_settings_glyph(surface, center, radius, color):
    cx, cy = center
    outer = max(6, int(radius * 0.48))
    inner = max(2, int(radius * 0.2))

    for angle in range(0, 360, 45):
        vec = pygame.math.Vector2(1, 0).rotate(angle)
        px = int(cx + vec.x * (outer + 2))
        py = int(cy + vec.y * (outer + 2))
        pygame.draw.circle(surface, color, (px, py), 2)

    pygame.draw.circle(surface, color, (cx, cy), outer, 2)
    pygame.draw.circle(surface, color, (cx, cy), inner)


def _draw_restart_glyph(surface, center, radius, color):
    cx, cy = center
    arc_rect = pygame.Rect(0, 0, int(radius * 1.5), int(radius * 1.5))
    arc_rect.center = center
    pygame.draw.arc(surface, color, arc_rect, 0.8, 5.75, 4)

    head = [
        (cx + int(radius * 0.56), cy - int(radius * 0.56)),
        (cx + int(radius * 0.2), cy - int(radius * 0.5)),
        (cx + int(radius * 0.45), cy - int(radius * 0.18)),
    ]
    pygame.draw.polygon(surface, color, head)


def _draw_home_glyph(surface, center, radius, color):
    cx, cy = center
    roof = [
        (cx, cy - int(radius * 0.58)),
        (cx - int(radius * 0.62), cy - int(radius * 0.02)),
        (cx + int(radius * 0.62), cy - int(radius * 0.02)),
    ]
    pygame.draw.polygon(surface, color, roof)

    body = pygame.Rect(0, 0, int(radius * 1.05), int(radius * 0.9))
    body.center = (cx, cy + int(radius * 0.35))
    pygame.draw.rect(surface, color, body, border_radius=2)

    door = pygame.Rect(0, 0, max(4, int(radius * 0.28)), max(7, int(radius * 0.46)))
    door.midbottom = body.midbottom
    pygame.draw.rect(surface, (86, 113, 136), door, border_radius=2)


def _draw_tutorial_glyph(surface, center, radius, color):
    font = pygame.font.SysFont("segoeui", max(12, int(radius * 0.95)), bold=True)
    text = font.render("?", True, color)
    surface.blit(text, text.get_rect(center=center))
