"""Simple blocking scene result types for transitional platform flow."""

from dataclasses import dataclass
from enum import Enum


class PlatformAction(str, Enum):
    HOME = "home"
    GAME_LIBRARY = "game_library"
    SETTINGS = "settings"
    ABOUT = "about"
    LEADERBOARD = "leaderboard"
    REWARDS = "rewards"
    LAUNCH_GAME = "launch_game"
    QUIT = "quit"


@dataclass(frozen=True)
class SceneResult:
    action: PlatformAction
    game_id: str | None = None
    payload: object | None = None
