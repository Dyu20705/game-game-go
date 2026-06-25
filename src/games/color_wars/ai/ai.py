from .ez_AI import get_ez_move
from .hard_AI import get_hard_move
from .med_AI import get_med_move


def get_ai_move(board, dots, difficulty):
    if difficulty in ("easy", "ez"):
        return get_ez_move(board, dots)
    if difficulty in ("medium", "med"):
        return get_med_move(board, dots)
    return get_hard_move(board, dots)
