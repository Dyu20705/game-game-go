"""Public game integration API for Game Game Go."""

from .contract import GameModule, GameSession
from .capability import GameCapability
from .descriptor import GameDescriptor
from .launch import GameExitAction, GameExitResult, GameLaunchOptions
from .registry import DuplicateGameError, GameNotFoundError, GameRegistry

__all__ = [
    "DuplicateGameError",
    "GameDescriptor",
    "GameCapability",
    "GameExitAction",
    "GameExitResult",
    "GameLaunchOptions",
    "GameModule",
    "GameNotFoundError",
    "GameRegistry",
    "GameSession",
]
