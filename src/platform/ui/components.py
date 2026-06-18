"""Tiny pygame UI helpers used by platform scenes."""

from src.platform.ui import theme


def draw_button(pygame, screen, rect, label, font, color=theme.PANEL_ALT, text_color=theme.TEXT):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (230, 238, 244), rect, 1, border_radius=8)
    text = font.render(label, True, text_color)
    screen.blit(text, text.get_rect(center=rect.center))


def draw_text(pygame, screen, font, text, center, color=theme.TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))

