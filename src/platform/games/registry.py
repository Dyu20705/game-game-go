"""Game registry used as the single source of truth for available games."""

from collections.abc import Iterable

from .contract import GameModule


class DuplicateGameError(ValueError):
    """Raised when two games try to use the same game_id."""


class GameNotFoundError(KeyError):
    """Raised when a requested game_id is not registered."""


class GameRegistry:
    """Register, resolve, and list mini-games."""

    def __init__(self):
        self._games: dict[str, GameModule] = {}

    def register(self, game: GameModule):
        game_id = game.descriptor.game_id
        if game_id in self._games:
            raise DuplicateGameError(f"Game id already registered: {game_id}")
        self._games[game_id] = game

    def get(self, game_id: str) -> GameModule:
        try:
            return self._games[game_id]
        except KeyError as exc:
            raise GameNotFoundError(f"Game is not registered: {game_id}") from exc

    def list_all(self) -> list[GameModule]:
        return self._sorted(self._games.values())

    def list_enabled(self) -> list[GameModule]:
        return self._sorted(game for game in self._games.values() if game.descriptor.enabled)

    @staticmethod
    def _sorted(games: Iterable[GameModule]) -> list[GameModule]:
        return sorted(games, key=lambda game: (game.descriptor.sort_order, game.descriptor.title, game.descriptor.game_id))

