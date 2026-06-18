"""SquareXO move types."""

from dataclasses import dataclass

from .state import Edge, Player


@dataclass(frozen=True)
class ClaimEdge:
    edge: Edge
    player: Player

