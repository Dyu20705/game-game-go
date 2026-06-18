"""Typed metadata for games registered in the platform."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GameDescriptor:
    """Stable public metadata displayed by the game library."""

    game_id: str
    title: str
    short_description: str
    version: str
    supported_modes: tuple[str, ...]
    thumbnail: Path | None = None
    enabled: bool = True
    sort_order: int = 100
    tags: tuple[str, ...] = field(default_factory=tuple)
    author: str | None = None
    min_players: int = 1
    max_players: int = 1

    def __post_init__(self):
        if not self.game_id:
            raise ValueError("GameDescriptor.game_id must not be empty")
        if not self.title:
            raise ValueError(f"GameDescriptor({self.game_id}) title must not be empty")
        if self.min_players < 1:
            raise ValueError(f"GameDescriptor({self.game_id}) min_players must be >= 1")
        if self.max_players < self.min_players:
            raise ValueError(f"GameDescriptor({self.game_id}) max_players must be >= min_players")

