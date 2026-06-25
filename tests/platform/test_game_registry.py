import pytest

from src.games.color_wars.game import ColorWarsGame
from src.games.demo_game.game import DemoGame
from src.platform.games import DuplicateGameError, GameNotFoundError, GameRegistry


def test_registry_lists_enabled_games_in_sort_order():
    registry = GameRegistry()
    registry.register(DemoGame())
    registry.register(ColorWarsGame())

    assert [game.descriptor.game_id for game in registry.list_enabled()] == ["color_wars", "demo_game"]


def test_registry_rejects_duplicate_ids():
    registry = GameRegistry()
    registry.register(ColorWarsGame())

    with pytest.raises(DuplicateGameError):
        registry.register(ColorWarsGame())


def test_registry_reports_missing_game():
    registry = GameRegistry()

    with pytest.raises(GameNotFoundError):
        registry.get("missing")
