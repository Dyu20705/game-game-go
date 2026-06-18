"""Choose game mode scene renderer."""

import pygame

from src.games.color_wars.view.commons import blit_fitted_text


def draw_choose_gamemode_scene(screen, panel, fonts, colors, rects, icons):
    """Draw mode selection scene."""
    screen.blit(icons["back"], rects["back_rect"].topleft)
    screen.blit(icons["settings"], rects["settings_icon_rect"].topleft)

    blit_fitted_text(
        screen,
        fonts["main"],
        "Chọn chế độ chơi",
        colors["title"],
        (panel.centerx, panel.y + int(panel.height * 0.24)),
        panel.width - 42,
        46,
    )

    def draw_mode_card(rect, icon_primary, icon_secondary, color):
        pygame.draw.rect(screen, (255, 248, 235), rect, border_radius=16)
        pygame.draw.rect(screen, color, rect, 3, border_radius=16)

        icon_size = min(max(20, rect.height // 2), max(28, rect.width // 4))
        row_y = int(rect.y + rect.height * 0.5)
        gap = max(16, icon_size // 2)
        left_x = rect.centerx - icon_size - gap
        right_x = rect.centerx + gap
        icon_left = pygame.transform.smoothscale(icon_primary, (icon_size, icon_size))
        icon_right = pygame.transform.smoothscale(icon_secondary, (icon_size, icon_size))
        screen.blit(icon_left, (left_x, row_y - icon_size // 2))
        screen.blit(icon_right, (right_x, row_y - icon_size // 2))

        vs_font = pygame.font.SysFont("segoeui", max(18, int(icon_size * 0.62)), bold=True)
        vs_text = vs_font.render("VS", True, (56, 67, 78))
        screen.blit(vs_text, vs_text.get_rect(center=(rect.centerx, row_y)))

    draw_mode_card(rects["pvp_btn"], icons["mode_pvp"], icons["mode_pvp"], colors["btn_blue"])
    draw_mode_card(rects["pvbot_btn"], icons["mode_pvp"], icons["mode_pvbot"], colors["btn_green"])


