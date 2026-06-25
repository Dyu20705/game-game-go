"""Heads-up display rendering."""

import pygame

from src.games.color_wars.engine.rules import PLAYER_BLUE
from src.games.color_wars.runtime.analysis import estimate_win_chances
from src.games.color_wars.view.commons import ensure_readable_text, suggest_safe_palette

from ..constants import BLUE_COLOR, HUD_TEXT_COLOR, RED_COLOR


def get_status_lines(game_mode=None, difficulty=None, winner=None):
    """Build status lines shown on the left HUD panel."""
    mode_name = "PvP" if game_mode == "pvp" else "PvE"
    if game_mode == "pvp":
        if winner is None:
            return [f"Chế độ: {mode_name}"]
        winner_name = "Xanh" if winner == PLAYER_BLUE else "Đỏ"
        return [f"Chế độ: {mode_name}", f"Thắng: {winner_name}"]

    difficulty_name = {
        "easy": "DỄ",
        "medium": "TRUNG BÌNH",
        "hard": "KHÓ",
    }.get((difficulty or "easy").lower(), (difficulty or "easy").upper())
    if winner is None:
        return [f"Chế độ: {mode_name}", f"Độ khó bot: {difficulty_name}"]

    winner_name = "Xanh" if winner == PLAYER_BLUE else "Đỏ"
    return [f"Chế độ: {mode_name}", f"Độ khó bot: {difficulty_name}", f"Thắng: {winner_name}"]


def get_control_lines():
    """Build controls shown on the right HUD panel."""
    return ["M: Đổi chế độ", "R: Chơi lại", "H: Hướng dẫn", "F11: Toàn màn hình"]


def get_move_history_entries(state, limit=6):
    """Return the most recent moves in display order."""
    entries = []
    for player, row, col in state.move_history[-limit:]:
        player_name = "B" if player == PLAYER_BLUE else "R"
        entries.append((player_name, f"({row + 1}, {col + 1})"))
    return entries


def _render_fitted_line(text, color, preferred_size, min_size, max_width):
    """Render a line that fits the available width."""
    font_size = preferred_size
    while font_size >= min_size:
        font = pygame.font.SysFont("consolas", font_size)
        surface = font.render(text, True, color)
        if surface.get_width() <= max_width:
            return surface
        font_size -= 1

    font = pygame.font.SysFont("consolas", min_size)
    if max_width <= 0:
        return font.render("", True, color)

    clipped = text
    while clipped:
        candidate = clipped + "..."
        surface = font.render(candidate, True, color)
        if surface.get_width() <= max_width:
            return surface
        clipped = clipped[:-1]

    return font.render("", True, color)


def drawScoreBadge(screen, layout, blue_score, red_score, current_player):
    """Draw the top-center score badge."""
    badge_w = max(180, int(layout["width"] * 0.26))
    badge_h = max(44, int(layout["height"] * 0.08))
    badge_x = (layout["width"] - badge_w) // 2
    badge_y = max(8, layout["side_margin"] // 2)

    badge_rect = pygame.Rect(badge_x, badge_y, badge_w, badge_h)
    turn_color = BLUE_COLOR if current_player == PLAYER_BLUE else RED_COLOR

    pygame.draw.ellipse(screen, (240, 240, 238), badge_rect)
    pygame.draw.ellipse(screen, turn_color, badge_rect, 4)

    score_font = pygame.font.SysFont("consolas", max(20, int(badge_h * 0.48)), bold=True)
    blue_text = score_font.render(str(blue_score), True, BLUE_COLOR)
    dot_text = score_font.render(" - ", True, (40, 40, 40))
    red_text = score_font.render(str(red_score), True, RED_COLOR)

    score_w = blue_text.get_width() + dot_text.get_width() + red_text.get_width()
    score_h = max(blue_text.get_height(), dot_text.get_height(), red_text.get_height())
    score_surface = pygame.Surface((score_w, score_h), pygame.SRCALPHA)
    x = 0
    score_surface.blit(blue_text, (x, 0))
    x += blue_text.get_width()
    score_surface.blit(dot_text, (x, 0))
    x += dot_text.get_width()
    score_surface.blit(red_text, (x, 0))

    sx = badge_x + (badge_w - score_surface.get_width()) // 2
    sy = badge_y + (badge_h - score_surface.get_height()) // 2
    screen.blit(score_surface, (sx, sy))


def _draw_panel(screen, rect, fill=(248, 242, 229), border=(216, 196, 170)):
    pygame.draw.rect(screen, fill, rect, border_radius=16)
    pygame.draw.rect(screen, border, rect, 2, border_radius=16)


def draw_win_rate_panel(screen, state, layout, game_mode=None, difficulty=None):
    """Draw a vertical probability bar on the right side like a chess-style evaluation meter."""
    width = layout["width"]
    height = layout["height"]
    start_x = layout["board_x"]
    start_y = layout["board_y"]
    board_size = layout["board_size"]
    side_margin = layout["side_margin"]

    panel_x = start_x + board_size + side_margin
    panel_w = width - panel_x - side_margin
    if panel_w < 90:
        return
    panel_h = max(210, int(height * 0.56))
    panel = pygame.Rect(panel_x, start_y, panel_w, panel_h)
    _draw_panel(screen, panel)

    title_font = pygame.font.SysFont("segoeui", max(15, int(height * 0.028)), bold=True)
    body_font = pygame.font.SysFont("segoeui", max(13, int(height * 0.024)), bold=True)
    title = title_font.render("Tỷ lệ thắng", True, HUD_TEXT_COLOR)
    screen.blit(title, (panel.x + 14, panel.y + 12))

    blue_chance, red_chance = estimate_win_chances(state)
    bar_rect = pygame.Rect(panel.x + 18, panel.y + 46, 22, panel.h - 60)
    pygame.draw.rect(screen, (232, 222, 208), bar_rect, border_radius=11)

    blue_height = int(bar_rect.height * (blue_chance / 100.0))
    red_height = bar_rect.height - blue_height
    blue_rect = pygame.Rect(bar_rect.x, bar_rect.y, bar_rect.width, blue_height)
    red_rect = pygame.Rect(bar_rect.x, bar_rect.bottom - red_height, bar_rect.width, red_height)
    if blue_height > 0:
        pygame.draw.rect(screen, BLUE_COLOR, blue_rect, border_radius=11)
    if red_height > 0:
        pygame.draw.rect(screen, RED_COLOR, red_rect, border_radius=11)

    pygame.draw.rect(screen, (130, 110, 92), bar_rect, 2, border_radius=11)

    blue_text = body_font.render(f"{blue_chance}%", True, BLUE_COLOR)
    red_text = body_font.render(f"{red_chance}%", True, RED_COLOR)
    screen.blit(blue_text, (bar_rect.right + 12, bar_rect.y - 2))
    screen.blit(red_text, (bar_rect.right + 12, bar_rect.bottom - red_text.get_height() + 2))


def draw_move_history_panel(screen, state, layout):
    """Draw recent moves in the lower-left area."""
    side_margin = layout["side_margin"]
    board_x = layout["board_x"]
    board_y = layout["board_y"]
    board_size = layout["board_size"]
    height = layout["height"]

    panel_w = board_x - side_margin * 2
    if panel_w < 100:
        return
    panel_h = min(190, max(120, int(height * 0.26)))
    panel_x = side_margin
    panel_y = min(height - panel_h - side_margin, board_y + board_size - panel_h)
    panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    _draw_panel(screen, panel)

    title_font = pygame.font.SysFont("segoeui", max(15, int(height * 0.028)), bold=True)
    item_font = pygame.font.SysFont("consolas", max(12, int(height * 0.022)))
    title = title_font.render("Nước đi gần đây", True, HUD_TEXT_COLOR)
    screen.blit(title, (panel.x + 14, panel.y + 12))

    entries = get_move_history_entries(state, limit=6)
    if not entries:
        empty = item_font.render("Chưa có nước đi", True, HUD_TEXT_COLOR)
        screen.blit(empty, (panel.x + 14, panel.y + 44))
        return

    start_y = panel.y + 42
    row_gap = max(18, item_font.get_height() + 4)
    for idx, (player_name, coord) in enumerate(entries):
        color = BLUE_COLOR if player_name == "B" else RED_COLOR
        line = item_font.render(f"{player_name}  {coord}", True, HUD_TEXT_COLOR)
        line_y = start_y + idx * row_gap
        if line_y + line.get_height() > panel.bottom - 8:
            break
        screen.blit(line, (panel.x + 14, line_y))
        pygame.draw.circle(screen, color, (panel.x + 10, line_y + line.get_height() // 2), 4)


def drawHud(screen, state, current_player, blue_score, red_score, winner, game_mode=None, difficulty=None, layout=None):
    """Draw the HUD areas around the board."""
    start_x = layout["board_x"]
    start_y = layout["board_y"]
    width = layout["width"]
    side_margin = layout["side_margin"]

    left_panel_width = start_x - side_margin * 2
    if left_panel_width < 80:
        left_panel_width = 0
    drawScoreBadge(screen, layout, blue_score, red_score, current_player)

    status_lines = get_status_lines(game_mode, difficulty, winner)

    palette = suggest_safe_palette()
    status_color = ensure_readable_text(palette["surface"], preferred=HUD_TEXT_COLOR)
    if left_panel_width > 0:
        left_x = side_margin
        left_y = start_y + 12
        line_step = max(20, int(layout["height"] * 0.036))
        for idx, line in enumerate(status_lines):
            line_surface = _render_fitted_line(
                line,
                status_color,
                preferred_size=max(16, int(layout["height"] * 0.032)),
                min_size=12,
                max_width=left_panel_width,
            )
            screen.blit(line_surface, (left_x, left_y + idx * line_step))

    draw_win_rate_panel(screen, state, layout, game_mode, difficulty)
    draw_move_history_panel(screen, state, layout)

    _ = width  # keep signature stable for callers using layout info
