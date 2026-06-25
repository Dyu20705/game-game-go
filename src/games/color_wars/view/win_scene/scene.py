"""Win scene overlay renderer."""

import pygame

from src.games.color_wars.engine.rules import PLAYER_BLUE
from src.games.color_wars.view.commons import blit_fitted_text, draw_interactive_button


def get_win_action_rects(screen):
    """Compute clickable controls for the end screen."""
    width, height = screen.get_size()
    panel_w = min(620, width - 36)
    panel_h = min(360, height - 36)
    panel = pygame.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)

    restart_rect = pygame.Rect(0, 0, 220, 56)
    restart_rect.center = (panel.centerx, panel.y + int(panel_h * 0.72))

    home_rect = pygame.Rect(0, 0, 150, 44)
    home_rect.center = (panel.centerx, panel.bottom - 40)

    return {
        "panel": panel,
        "restart_rect": restart_rect,
        "home_rect": home_rect,
    }


def draw_win_scene(screen, winner, icons):
    """Draw full-screen win scene and return action rects."""
    if winner is None:
        return {}

    rects = get_win_action_rects(screen)
    panel = rects["panel"]
    restart_rect = rects["restart_rect"]
    home_rect = rects["home_rect"]

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((8, 16, 26, 150))
    screen.blit(shade, (0, 0))

    pygame.draw.rect(screen, (28, 39, 53), panel, border_radius=18)
    pygame.draw.rect(screen, (160, 185, 208), panel, 3, border_radius=18)

    accent = (46, 125, 193) if winner == PLAYER_BLUE else (206, 79, 79)
    title_font = pygame.font.SysFont("segoeui", max(34, int(panel.height * 0.13)), bold=True)
    body_font = pygame.font.SysFont("segoeui", max(18, int(panel.height * 0.07)), bold=True)
    button_font = pygame.font.SysFont("segoeui", 30, bold=True)
    small_button_font = pygame.font.SysFont("segoeui", 22, bold=True)

    winner_name = "NGƯỜI CHƠI XANH" if winner == PLAYER_BLUE else "NGƯỜI CHƠI ĐỎ"
    blit_fitted_text(
        screen,
        title_font,
        "TRẬN ĐÃ KẾT THÚC",
        (240, 247, 255),
        (panel.centerx, panel.y + 64),
        panel.width - 30,
        56,
    )
    blit_fitted_text(
        screen,
        body_font,
        f"Bên thắng: {winner_name}",
        accent,
        (panel.centerx, panel.y + 118),
        panel.width - 44,
        42,
    )
    blit_fitted_text(
        screen,
        body_font,
        "TIẾP ĐÊ SỢ À?",
        (198, 216, 232),
        (panel.centerx, panel.y + 156),
        panel.width - 44,
        38,
    )

    draw_interactive_button(
        screen,
        restart_rect,
        "CHƠI LẠI",
        accent,
        button_font,
        border_radius=14,
    )
    draw_interactive_button(
        screen,
        home_rect,
        "TRANG CHỦ",
        (95, 122, 147),
        small_button_font,
        border_radius=12,
    )

    return rects
