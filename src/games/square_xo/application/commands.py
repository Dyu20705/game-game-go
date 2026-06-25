"""SquareXO application commands."""

from dataclasses import dataclass

from src.games.square_xo.domain.state import Edge, Player


@dataclass(frozen=True)
class ClaimEdgeCommand:
    edge: Edge
    player: Player
