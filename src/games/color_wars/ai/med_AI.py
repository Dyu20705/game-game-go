import random

from src.games.color_wars.engine.explosion import resolve_explosions
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED, get_move_dot_increment, get_valid_moves

MED_TOP_K = 3
MED_TIE_NOISE_THRESHOLD = 0.55
MED_TOP_RANDOM_PROB = 0.24
MED_RANDOM_POOL = 3


def _material_score(board):
    score = 0
    for row in board:
        for cell in row:
            if cell == PLAYER_RED:
                score += 1
            elif cell == PLAYER_BLUE:
                score -= 1
    return score


def _mobility_score(board):
    red_moves = len(get_valid_moves(board, PLAYER_RED))
    blue_moves = len(get_valid_moves(board, PLAYER_BLUE))
    return red_moves - blue_moves


def evaluate_board(board, dots):
    """Evaluate board state for Red (AI). Higher score means better for AI."""
    material = _material_score(board)
    mobility = _mobility_score(board)

    red_dots = 0
    blue_dots = 0
    for r in range(len(board)):
        for c in range(len(board[r])):
            if board[r][c] == PLAYER_RED:
                red_dots += dots[r][c]
            elif board[r][c] == PLAYER_BLUE:
                blue_dots += dots[r][c]

    return material * 3.0 + mobility * 1.5 + (red_dots - blue_dots) * 0.2


def simulate_move(board, dots, move):
    """Return a copied board/dots after applying move for Red and resolving chain explosions."""
    row, col = move
    board_copy = [line[:] for line in board]
    dots_copy = [line[:] for line in dots]

    increment = get_move_dot_increment(board_copy, row, col)
    board_copy[row][col] = PLAYER_RED
    dots_copy[row][col] += increment
    resolve_explosions(board_copy, dots_copy, row, col)

    return board_copy, dots_copy


def get_move_score(board, dots, move):
    next_board, next_dots = simulate_move(board, dots, move)
    return evaluate_board(next_board, next_dots)


def get_top_moves(board, dots):
    moves = get_valid_moves(board, PLAYER_RED)
    if not moves:
        return []

    move_scores = [(move, get_move_score(board, dots, move)) for move in moves]
    move_scores.sort(key=lambda item: item[1], reverse=True)
    return move_scores


def _response_score(board, dots, move):
    next_board, next_dots = simulate_move(board, dots, move)
    replies = get_valid_moves(next_board, PLAYER_BLUE)
    if not replies:
        return evaluate_board(next_board, next_dots)

    worst_reply = None
    worst_score = None
    for reply in replies:
        reply_board, reply_dots = simulate_move(next_board, next_dots, reply)
        score = evaluate_board(reply_board, reply_dots)
        if worst_score is None or score < worst_score:
            worst_score = score
            worst_reply = reply

    return worst_score if worst_reply is not None else evaluate_board(next_board, next_dots)


def get_med_move(board, dots):
    """Medium AI: shallow lookahead with a small amount of tie-breaking noise."""
    scored_moves = get_top_moves(board, dots)
    if not scored_moves:
        return None

    # Keep medium strength bounded by considering only a few top candidate moves.
    response_scores = []
    for move, _ in scored_moves[:MED_TOP_K]:
        response_scores.append((move, _response_score(board, dots, move)))

    response_scores.sort(key=lambda item: item[1], reverse=True)
    if len(response_scores) == 1:
        return response_scores[0][0]

    best_move, best_score = response_scores[0]
    random_pool = [move for move, _ in response_scores[: min(MED_RANDOM_POOL, len(response_scores))]]

    if random_pool and random.random() < MED_TOP_RANDOM_PROB:
        return random.choice(random_pool)

    _, second_score = response_scores[1]
    if abs(best_score - second_score) <= MED_TIE_NOISE_THRESHOLD:
        second_move = response_scores[1][0]
        return random.choice([best_move, second_move])
    return best_move
