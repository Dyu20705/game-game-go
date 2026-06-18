"""Easy AI for Red: intentionally weak and beginner-friendly."""

import random

from src.games.color_wars.engine.explosion import resolve_explosions
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED, get_move_dot_increment, get_valid_moves


EZ_WEAK_PICK_PROB = 0.80


def _simulate_move(board, dots, move):
    row, col = move
    board_copy = [line[:] for line in board]
    dots_copy = [line[:] for line in dots]

    increment = get_move_dot_increment(board_copy, row, col)
    board_copy[row][col] = PLAYER_RED
    dots_copy[row][col] += increment
    resolve_explosions(board_copy, dots_copy, row, col)
    return board_copy


def _material_score(board):
    score = 0
    for row in board:
        for cell in row:
            if cell == PLAYER_RED:
                score += 1
            elif cell == PLAYER_BLUE:
                score -= 1
    return score


def _worst_half_moves(board, dots, moves):
    """Return lower-impact moves to keep Easy mode forgiving for new players."""
    scored = [(move, _material_score(_simulate_move(board, dots, move))) for move in moves]
    scored.sort(key=lambda item: item[1])

    half = max(1, len(scored) // 2)
    return [move for move, _ in scored[:half]]


def get_ez_move(board, dots):
    """Pick mostly weak moves so beginners can learn without being crushed."""
    moves = get_valid_moves(board, PLAYER_RED)
    if not moves:
        return None

    if len(moves) > 1 and random.random() < EZ_WEAK_PICK_PROB:
        weaker_moves = _worst_half_moves(board, dots, moves)
        return random.choice(weaker_moves)

    return random.choice(moves)

