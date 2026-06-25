"""Gameplay scene composer."""

from src.games.color_wars.engine.rules import PLAYER_BLUE

from ..constants import BG_BLUE_TURN, BG_NEUTRAL, BG_RED_TURN
from ..layout import compute_layout
from .board import drawBoard
from .hud import drawHud


def draw_gameplay_scene(
    screen, state, board, dots, current_player, blue_score, red_score, winner, game_mode=None, difficulty=None
):
    """Render one complete gameplay frame with optional win overlay."""
    layout = compute_layout(screen, len(board))
    if winner is None:
        bg_color = BG_BLUE_TURN if current_player == PLAYER_BLUE else BG_RED_TURN
    else:
        bg_color = BG_NEUTRAL

    screen.fill(bg_color)
    drawBoard(screen, board, dots, layout)
    drawHud(screen, state, current_player, blue_score, red_score, winner, game_mode, difficulty, layout)


def drawScene(
    screen, state, board, dots, current_player, blue_score, red_score, winner, game_mode=None, difficulty=None
):
    """Compatibility wrapper for previous API name."""
    draw_gameplay_scene(
        screen, state, board, dots, current_player, blue_score, red_score, winner, game_mode, difficulty
    )
