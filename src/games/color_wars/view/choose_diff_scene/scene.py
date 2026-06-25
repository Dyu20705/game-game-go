"""Choose difficulty scene renderer."""

import pygame

from src.games.color_wars.view.commons import blit_fitted_text


def draw_choose_diff_scene(screen, panel, fonts, colors, rects, difficulty, icons):
    """Draw difficulty picker scene."""
    screen.blit(icons["back"], rects["back_rect"].topleft)
    screen.blit(icons["settings"], rects["settings_icon_rect"].topleft)

    current_color = colors["diff_colors"][difficulty]
    icon = icons[difficulty]
    screen.blit(icon, icon.get_rect(center=(panel.centerx, panel.y + 170)))

    localized_diff = {
        "easy": "DỄ",
        "medium": "TRUNG BÌNH",
        "hard": "KHÓ",
    }.get(difficulty, difficulty.upper())
    blit_fitted_text(
        screen,
        fonts["main"],
        localized_diff,
        current_color,
        (panel.centerx, panel.y + 270),
        panel.width - 42,
        52,
    )

    slider_rect = rects["slider_rect"]
    knob_x = rects["knob_x"]
    pygame.draw.rect(screen, (218, 226, 232), slider_rect, border_radius=14)
    fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, max(1, knob_x - slider_rect.x), slider_rect.height)
    pygame.draw.rect(screen, current_color, fill_rect, border_radius=14)
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 15)
    pygame.draw.circle(screen, current_color, (knob_x, slider_rect.centery), 11)

    blit_fitted_text(
        screen,
        fonts["body"],
        "Kéo thanh trượt để chọn độ khó của bot",
        colors["subtitle"],
        (panel.centerx, slider_rect.bottom + 28),
        panel.width - 60,
        28,
    )

    rects["draw_button"](screen, rects["play_match_btn"], "BẮT ĐẦU", current_color, fonts["button"])
