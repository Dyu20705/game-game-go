"""Launch options and exit results shared by all mini-games."""

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class GameExitAction(str, Enum):
    """Where platform control should go after a game session exits."""

    GAME_LIBRARY = "game_library"
    HOME = "home"
    RESTART = "restart"
    QUIT = "quit"


@dataclass(frozen=True)
class GameLaunchOptions:
    """Common launch data with a typed escape hatch for game-specific options."""

    mode: str | None = None
    difficulty: str | None = None
    custom: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "custom", MappingProxyType(dict(self.custom)))


@dataclass(frozen=True)
class GameExitResult:
    """Result returned by a mini-game when it gives control back to the platform."""

    action: GameExitAction = GameExitAction.GAME_LIBRARY
    payload: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))
