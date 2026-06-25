from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto

ColorKey = str
StackState = tuple[tuple[ColorKey, ...], ...]


class GameMode(Enum):
    IDLE = auto()
    SOURCE_SELECTED = auto()
    MOVING = auto()
    COMPLETED = auto()


@dataclass
class Screw:
    target_color: ColorKey | None
    capacity: int
    nuts: list[ColorKey] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.nuts

    def is_full(self) -> bool:
        return len(self.nuts) >= self.capacity

    def top_nut(self) -> ColorKey | None:
        return self.nuts[-1] if self.nuts else None

    def copy(self) -> "Screw":
        return Screw(self.target_color, self.capacity, self.nuts.copy())


@dataclass(frozen=True)
class Difficulty:
    key: str
    label: str
    color_count: int
    capacity: int
    spare_count: int
    scramble_moves: int


DIFFICULTIES: dict[str, Difficulty] = {
    "easy": Difficulty("easy", "Easy", 3, 3, 2, 36),
    "normal": Difficulty("normal", "Normal", 4, 4, 2, 88),
    "hard": Difficulty("hard", "Hard", 5, 4, 1, 148),
}

COLOR_ORDER: tuple[ColorKey, ...] = (
    "red",
    "blue",
    "yellow",
    "green",
    "purple",
    "orange",
)

COLOR_NAMES: dict[ColorKey, str] = {
    "red": "Red",
    "blue": "Blue",
    "yellow": "Yellow",
    "green": "Green",
    "purple": "Purple",
    "orange": "Orange",
}
