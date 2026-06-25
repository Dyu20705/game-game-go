"""Small pygame UI components used by platform scenes."""

from __future__ import annotations

from dataclasses import dataclass

from src.platform.ui import theme


@dataclass(frozen=True)
class ButtonState:
    hovered: bool = False
    pressed: bool = False
    disabled: bool = False
    focused: bool = False
    selected: bool = False


def draw_button(
    pygame,
    screen,
    rect,
    label,
    font,
    color=theme.PANEL_ALT,
    text_color=theme.TEXT,
    *,
    state: ButtonState | None = None,
):
    state = state or ButtonState()
    fill = color
    border = theme.BORDER_SUBTLE
    label_color = text_color
    if state.disabled:
        fill = theme.SIDEBAR
        border = theme.BORDER_SUBTLE
        label_color = theme.SUBTLE
    elif state.selected:
        fill = theme.PRIMARY
        border = theme.FOCUS
        label_color = (255, 255, 255)
    elif state.pressed:
        fill = theme.BRAND_PRIMARY_HOVER
        border = theme.FOCUS
    elif state.hovered:
        fill = theme.HOVER if color == theme.PANEL_ALT else theme.BRAND_PRIMARY_HOVER
        border = theme.BORDER

    pygame.draw.rect(screen, theme.SHADOW_MD[:3], rect.move(0, 3), border_radius=theme.RADIUS_MD)
    pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MD)
    pygame.draw.rect(screen, border, rect, 2 if state.focused else 1, border_radius=theme.RADIUS_MD)
    if state.focused:
        draw_focus_ring(pygame, screen, rect)
    draw_text(pygame, screen, font, label, rect.center, label_color)


def draw_icon_button(pygame, screen, rect, icon_label, font, *, state: ButtonState | None = None):
    draw_button(pygame, screen, rect, icon_label, font, color=theme.PANEL_ALT, state=state)


def draw_pill(pygame, screen, rect, label, font, fill, text_color=theme.TEXT, border=None):
    pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_PILL)
    if border:
        pygame.draw.rect(screen, border, rect, 1, border_radius=theme.RADIUS_PILL)
    draw_text(pygame, screen, font, label, rect.center, text_color)


def draw_focus_ring(pygame, screen, rect):
    pygame.draw.rect(screen, theme.FOCUS, rect.inflate(6, 6), 2, border_radius=theme.RADIUS_MD)


def draw_text(pygame, screen, font, text, center, color=theme.TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, surface.get_rect(center=center))
    return surface


def draw_status_message(pygame, screen, rect, message, font, *, kind: str = "neutral"):
    color = {
        "success": theme.SUCCESS,
        "warning": theme.WARNING,
        "danger": theme.DANGER,
        "error": theme.DANGER,
    }.get(kind, theme.PANEL)
    pygame.draw.rect(screen, color, rect, border_radius=theme.RADIUS_MD)
    pygame.draw.rect(screen, theme.BORDER_SUBTLE, rect, 1, border_radius=theme.RADIUS_MD)
    draw_text(pygame, screen, font, message, rect.center, theme.TEXT)


def draw_loading_indicator(pygame, screen, center, radius, color=theme.PRIMARY):
    x, y = center
    pygame.draw.circle(screen, color, (x, y), radius, 2)
    pygame.draw.circle(screen, theme.WARNING, (x + radius // 2, y - radius // 2), max(2, radius // 5))
