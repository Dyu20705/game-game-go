"""SquareXO deterministic domain API."""

from .board import create_game, edge_key, is_edge_taken, legal_edges
from .move import ClaimEdge
from .rules import apply_move
from .state import Edge, Player, Point, SquareXOState

__all__ = [
    "ClaimEdge",
    "Edge",
    "Player",
    "Point",
    "SquareXOState",
    "apply_move",
    "create_game",
    "edge_key",
    "is_edge_taken",
    "legal_edges",
]
