import random

from src.games.color_wars.engine.explosion import resolve_explosions
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED, get_move_dot_increment, get_valid_moves

INF = 10**9
BASE_DEPTH = 1
LATE_GAME_DEPTH = 1
LATE_GAME_BRANCH_THRESHOLD = 5
MOVE_ORDER_TOP_K = 3
POSITION_WEIGHT = 0.15
WIN_SCORE = 10**6
IMMEDIATE_LOSS_PENALTY = 10**5
HARD_TOP_RANDOM_PROB = 0.10
HARD_RANDOM_POOL = 2


def _simulate_move(board, dots, move, player):
    row, col = move
    board_copy = [line[:] for line in board]
    dots_copy = [line[:] for line in dots]

    inc = get_move_dot_increment(board_copy, row, col)
    board_copy[row][col] = player
    dots_copy[row][col] += inc
    resolve_explosions(board_copy, dots_copy, row, col)
    return board_copy, dots_copy


def _normalized_features(board, dots):
    size = len(board)
    total = max(1, size * size)
    center = (size - 1) / 2.0
    max_dist = max(1.0, center * 2.0)

    red_cells = 0
    blue_cells = 0
    red_dots = 0
    blue_dots = 0
    red_threat = 0
    blue_threat = 0
    red_stable = 0
    blue_stable = 0
    position_norm = 0.0

    for r in range(size):
        for c in range(size):
            cell = board[r][c]
            dot = dots[r][c]
            dist = abs(r - center) + abs(c - center)
            proximity = 1.0 - (dist / max_dist)
            if cell == PLAYER_RED:
                red_cells += 1
                red_dots += dot
                position_norm += proximity
                if dot >= 3:
                    red_threat += 1
                if dot <= 1:
                    red_stable += 1
            elif cell == PLAYER_BLUE:
                blue_cells += 1
                blue_dots += dot
                position_norm -= proximity
                if dot >= 3:
                    blue_threat += 1
                if dot <= 1:
                    blue_stable += 1

    material_norm = (red_cells - blue_cells) / total
    mobility_norm = (len(get_valid_moves(board, PLAYER_RED)) - len(get_valid_moves(board, PLAYER_BLUE))) / total
    threat_norm = (red_threat - blue_threat) / total
    danger_norm = blue_threat / total
    stability_norm = (red_stable - blue_stable) / total
    dot_norm = (red_dots - blue_dots) / (total * 4.0)
    position_norm /= total

    return material_norm, mobility_norm, threat_norm, danger_norm, stability_norm, dot_norm, position_norm


def evaluate_board(board, dots):
    material_norm, mobility_norm, threat_norm, danger_norm, stability_norm, dot_norm, position_norm = (
        _normalized_features(board, dots)
    )
    return (
        1.50 * material_norm
        + 0.70 * mobility_norm
        + 0.80 * threat_norm
        - 0.90 * danger_norm
        + 0.45 * stability_norm
        + 0.20 * dot_norm
        + POSITION_WEIGHT * position_norm
    )


def _count_cells(board):
    red_cells = 0
    blue_cells = 0
    for row in board:
        for cell in row:
            if cell == PLAYER_RED:
                red_cells += 1
            elif cell == PLAYER_BLUE:
                blue_cells += 1
    return red_cells, blue_cells


def _updated_initialized_flags(board, red_initialized, blue_initialized):
    red_cells, blue_cells = _count_cells(board)
    return red_initialized or red_cells > 0, blue_initialized or blue_cells > 0


def _winner_from_board(board, red_initialized, blue_initialized):
    size = len(board)
    total = size * size
    red_cells, blue_cells = _count_cells(board)

    if red_cells == total:
        return PLAYER_RED
    if blue_cells == total:
        return PLAYER_BLUE
    if red_initialized and red_cells == 0 and blue_cells > 0:
        return PLAYER_BLUE
    if blue_initialized and blue_cells == 0 and red_cells > 0:
        return PLAYER_RED
    return None


def _position_score(board, dots, red_initialized, blue_initialized):
    winner = _winner_from_board(board, red_initialized, blue_initialized)
    if winner == PLAYER_RED:
        return WIN_SCORE
    if winner == PLAYER_BLUE:
        return -WIN_SCORE
    return evaluate_board(board, dots)


def _can_player_win_next(board, dots, player, red_initialized, blue_initialized):
    moves = get_valid_moves(board, player)
    if not moves:
        return False

    for move in moves:
        nboard, ndots = _simulate_move(board, dots, move, player)
        nred_initialized, nblue_initialized = _updated_initialized_flags(nboard, red_initialized, blue_initialized)
        if _winner_from_board(nboard, nred_initialized, nblue_initialized) == player:
            return True

    return False


def _score_move(board, dots, move, player, red_initialized, blue_initialized):
    next_board, next_dots = _simulate_move(board, dots, move, player)
    next_red_initialized, next_blue_initialized = _updated_initialized_flags(
        next_board, red_initialized, blue_initialized
    )

    score_red_perspective = _position_score(next_board, next_dots, next_red_initialized, next_blue_initialized)
    player_score = score_red_perspective if player == PLAYER_RED else -score_red_perspective

    opponent = PLAYER_BLUE if player == PLAYER_RED else PLAYER_RED
    if _can_player_win_next(next_board, next_dots, opponent, next_red_initialized, next_blue_initialized):
        player_score -= IMMEDIATE_LOSS_PENALTY

    return player_score


def _ordered_moves(board, dots, player, top_k, red_initialized, blue_initialized):
    moves = get_valid_moves(board, player)
    if not moves:
        return []

    scored = [(move, _score_move(board, dots, move, player, red_initialized, blue_initialized)) for move in moves]
    scored.sort(key=lambda item: item[1], reverse=True)
    return [move for move, _ in scored[: min(top_k, len(scored))]]


def _alphabeta(board, dots, depth, alpha, beta, player, red_initialized, blue_initialized):
    terminal = _winner_from_board(board, red_initialized, blue_initialized)
    if terminal == PLAYER_RED:
        return WIN_SCORE, None
    if terminal == PLAYER_BLUE:
        return -WIN_SCORE, None

    if depth == 0:
        return evaluate_board(board, dots), None

    moves = get_valid_moves(board, player)
    next_player = PLAYER_BLUE if player == PLAYER_RED else PLAYER_RED
    if not moves:
        return _alphabeta(board, dots, depth - 1, alpha, beta, next_player, red_initialized, blue_initialized)

    ordered = _ordered_moves(board, dots, player, MOVE_ORDER_TOP_K, red_initialized, blue_initialized)

    if player == PLAYER_RED:
        best_score = -INF
        best_move = None
        for move in ordered:
            nboard, ndots = _simulate_move(board, dots, move, player)
            nred_initialized, nblue_initialized = _updated_initialized_flags(nboard, red_initialized, blue_initialized)
            score, _ = _alphabeta(
                nboard,
                ndots,
                depth - 1,
                alpha,
                beta,
                next_player,
                nred_initialized,
                nblue_initialized,
            )
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)
            if alpha >= beta:
                break
        return best_score, best_move

    best_score = INF
    best_move = None
    for move in ordered:
        nboard, ndots = _simulate_move(board, dots, move, player)
        nred_initialized, nblue_initialized = _updated_initialized_flags(nboard, red_initialized, blue_initialized)
        score, _ = _alphabeta(
            nboard,
            ndots,
            depth - 1,
            alpha,
            beta,
            next_player,
            nred_initialized,
            nblue_initialized,
        )
        if score < best_score:
            best_score = score
            best_move = move
        beta = min(beta, best_score)
        if alpha >= beta:
            break
    return best_score, best_move


def get_hard_move(board, dots):
    """Choose the strongest move found by an adaptive-depth alpha-beta search."""
    moves = get_valid_moves(board, PLAYER_RED)
    if not moves:
        return None

    if len(moves) == 1:
        return moves[0]

    red_initialized, blue_initialized = _updated_initialized_flags(board, False, False)
    random_pool = _ordered_moves(
        board,
        dots,
        PLAYER_RED,
        HARD_RANDOM_POOL,
        red_initialized,
        blue_initialized,
    )
    if random_pool and random.random() < HARD_TOP_RANDOM_PROB:
        return random.choice(random_pool)

    depth = LATE_GAME_DEPTH if len(moves) <= LATE_GAME_BRANCH_THRESHOLD else BASE_DEPTH
    _, best_move = _alphabeta(
        board,
        dots,
        depth,
        -INF,
        INF,
        PLAYER_RED,
        red_initialized,
        blue_initialized,
    )
    return best_move if best_move in moves else moves[0]
