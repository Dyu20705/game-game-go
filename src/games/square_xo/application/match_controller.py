"""Application-level controller for SquareXO."""

from src.games.square_xo.domain.move import ClaimEdge
from src.games.square_xo.domain.rules import apply_move


class SquareXOMatchController:
    def __init__(self, state):
        self.state = state
        self.moves: list[ClaimEdge] = []

    def claim_edge(self, move: ClaimEdge):
        self.state = apply_move(self.state, move)
        self.moves.append(move)
        return self.state

