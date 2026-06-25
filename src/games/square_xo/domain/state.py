"""SquareXO deterministic domain state."""

from dataclasses import dataclass, field
from enum import Enum


class Player(str, Enum):
    X = "X"
    O = "O"

    def next(self):
        return Player.O if self == Player.X else Player.X


@dataclass(frozen=True, order=True)
class Point:
    row: int
    col: int


@dataclass(frozen=True)
class Edge:
    from_point: Point
    to_point: Point
    taken_by: Player | None = None


@dataclass(frozen=True)
class BoxClaim:
    row: int
    col: int
    owner: Player


@dataclass(frozen=True)
class SquareXOState:
    rows: int
    cols: int
    edges: tuple[Edge, ...]
    boxes: tuple[BoxClaim, ...] = field(default_factory=tuple)
    current_player: Player = Player.X
    score_x: int = 0
    score_o: int = 0

    @property
    def score(self) -> dict[str, int]:
        return {"X": self.score_x, "O": self.score_o}

    @property
    def is_terminal(self) -> bool:
        return all(edge.taken_by is not None for edge in self.edges)

    @property
    def winner(self) -> Player | None:
        if not self.is_terminal or self.score_x == self.score_o:
            return None
        return Player.X if self.score_x > self.score_o else Player.O
