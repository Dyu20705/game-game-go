"""Lightweight gameplay analysis helpers for HUD statistics."""

from math import tanh

from src.games.color_wars.controller import get_scores
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED, get_valid_moves


def _sum_dots(state, owner):
    total = 0
    for row in range(state.grid_size):
        for col in range(state.grid_size):
            if state.board[row][col] == owner:
                total += state.dots[row][col]
    return total


def estimate_win_chances(state):
    """Estimate blue/red win chance with phase-aware normalized heuristics."""
    if state.winner == PLAYER_BLUE:
        return 100.0, 0.0
    if state.winner == PLAYER_RED:
        return 0.0, 100.0

    blue_cells, red_cells = get_scores(state)
    blue_dots = _sum_dots(state, PLAYER_BLUE)
    red_dots = _sum_dots(state, PLAYER_RED)
    blue_moves = len(get_valid_moves(state.board, PLAYER_BLUE))
    red_moves = len(get_valid_moves(state.board, PLAYER_RED))

    blue_hot = 0
    red_hot = 0
    for row in range(state.grid_size):
        for col in range(state.grid_size):
            owner = state.board[row][col]
            if owner == PLAYER_BLUE and state.dots[row][col] >= 3:
                blue_hot += 1
            elif owner == PLAYER_RED and state.dots[row][col] >= 3:
                red_hot += 1

    total_cells = max(1, state.grid_size * state.grid_size)
    total_dots = max(1, blue_dots + red_dots)
    total_moves = max(1, blue_moves + red_moves)
    total_hot = max(1, blue_hot + red_hot)

    territory_diff = (blue_cells - red_cells) / total_cells
    dot_diff = (blue_dots - red_dots) / total_dots
    mobility_diff = (blue_moves - red_moves) / total_moves
    hot_diff = (blue_hot - red_hot) / total_hot

    phase = min(1.0, state.turn_count / 14.0)
    territory_w = 0.42 + 0.26 * phase
    dot_w = 0.18 + 0.16 * phase
    mobility_w = 0.30 - 0.16 * phase
    hot_w = 0.10

    score = territory_diff * territory_w + dot_diff * dot_w + mobility_diff * mobility_w + hot_diff * hot_w

    if abs(score) < 1e-9:
        return 50.0, 50.0

    blue_chance = 50.0 + 50.0 * tanh(score * 2.4)
    blue_chance = max(3.0, min(97.0, blue_chance))
    red_chance = 100.0 - blue_chance
    return round(blue_chance, 1), round(red_chance, 1)


def format_cell_label(row, col):
    """Render a board coordinate as A1 style label."""
    if row is None or col is None:
        return "-"
    return f"{chr(ord('A') + col)}{row + 1}"
