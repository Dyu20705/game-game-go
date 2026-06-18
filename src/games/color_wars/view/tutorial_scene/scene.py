"""Tutorial scene and icon renderer."""

import pygame

from src.games.color_wars.view.commons import blit_fitted_text, make_icon_surface


def draw_tutorial_icon(screen, rect, colors, font=None):
    """Draw tutorial icon using the shared icon style."""
    icon = make_icon_surface("tutorial", rect.size, bg_color=colors["btn_amber"])
    screen.blit(icon, rect.topleft)


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
    lowered = line.lower()
    if "nổ dây chuyền" in lowered or "combo" in lowered:
        return (255, 208, 132)
    if "4 chấm" in lowered:
        return (255, 188, 120)
    if "phím tắt" in lowered:
        return (166, 216, 255)
    return (238, 246, 255)


def draw_tutorial_scene(screen, panel, fonts, colors, back_rect, tutorial_lines, back_icon):
    """Draw tutorial content scene."""
    screen.blit(back_icon, back_rect.topleft)
    blit_fitted_text(
        screen,
        fonts["main"],
        "Cách chơi",
        colors["text_main"],
        (panel.centerx, panel.y + 84),
        panel.width - 48,
        50,
    )
    blit_fitted_text(
        screen,
        fonts["body"],
        "Cơ chế cơ bản, mẹo chiến thuật và phím tắt",
        colors["subtitle"],
        (panel.centerx, panel.y + 120),
        panel.width - 64,
        32,
    )

    line_y = panel.y + 156
    max_width = panel.width - 120
    for idx, line in enumerate(tutorial_lines, start=1):
        rendered_color = _line_color(line)
        wrapped = _render_wrapped_lines(fonts["body"], f"{idx}. {line}", rendered_color, max_width)
        for text in wrapped:
            screen.blit(text, text.get_rect(center=(panel.centerx, line_y + text.get_height() // 2)))
            line_y += max(22, int(panel.height * 0.05))
        line_y += 10


