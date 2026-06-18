"""Create SquareXO matches."""

from src.games.square_xo.domain.board import create_game


def create_local_match(rows: int = 4, cols: int = 4):
    return create_game(rows, cols)

