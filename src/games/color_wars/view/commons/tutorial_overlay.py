"""Reusable tutorial overlay that can be drawn on top of any scene."""

import pygame

from src.games.color_wars.view.commons.ui_components import blit_fitted_text, draw_interactive_button


def _render_wrapped_lines(font, text, color, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(font.render(current, True, color))
        current = word
    if current:
        lines.append(font.render(current, True, color))
    return lines


def _line_color(line):
    """Highlight key tutorial phrases for faster scanning."""
    lowered = line.lower()
    if "nổ dây chuyền" in lowered or "combo" in lowered:
        return (255, 208, 132)
    if "4 chấm" in lowered:
        return (255, 188, 120)
    if "phím tắt" in lowered:
        return (166, 216, 255)
    return (238, 246, 255)


def draw_tutorial_overlay(screen, panel, fonts, colors, lines, close_label="Đóng"):
    """Draw translucent overlay with beginner tutorial content.

    Returns:
        dict containing close button rect.
    """
    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((8, 16, 26, 150))
    screen.blit(shade, (0, 0))

    overlay_w = max(int(screen.get_width() * 0.78), min(int(panel.width * 1.45), screen.get_width() - 32))
    overlay_h = max(int(screen.get_height() * 0.82), min(int(panel.height * 1.2), screen.get_height() - 32))
    overlay = pygame.Rect(
        (screen.get_width() - overlay_w) // 2,
        (screen.get_height() - overlay_h) // 2,
        overlay_w,
        overlay_h,
    )

    pygame.draw.rect(screen, (28, 39, 53), overlay, border_radius=18)
    pygame.draw.rect(screen, (160, 185, 208), overlay, 3, border_radius=18)

    blit_fitted_text(
        screen,
        fonts["main"],
        "Hướng dẫn nhanh",
        (240, 247, 255),
        (overlay.centerx, overlay.y + 48),
        overlay.width - 42,
        52,
    )
    blit_fitted_text(
        screen,
        fonts["body"],
        "Tổng quan cho người mới",
        (198, 216, 232),
        (overlay.centerx, overlay.y + 84),
        overlay.width - 42,
        34,
    )

    text_max_width = overlay.width - 120
    line_y = overlay.y + 126
    step_idx = 1
    for line in lines:
        rendered_color = _line_color(line)
        wrapped = _render_wrapped_lines(fonts["body"], f"{step_idx}. {line}", rendered_color, text_max_width)
        for text in wrapped:
            if line_y + text.get_height() > overlay.bottom - 64:
                break
            screen.blit(text, text.get_rect(center=(overlay.centerx, line_y + text.get_height() // 2)))
            line_y += max(21, int(overlay.height * 0.05))
        line_y += 10
        step_idx += 1
        if line_y > overlay.bottom - 64:
            break

    close_rect = pygame.Rect(overlay.right - 128, overlay.bottom - 48, 96, 32)
    draw_interactive_button(screen, close_rect, close_label, (66, 146, 212), fonts["body"], border_radius=8)

    return {"overlay": overlay, "close_rect": close_rect}


