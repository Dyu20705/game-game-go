from types import SimpleNamespace

from src.games.color_wars.game import ColorWarsGame, ColorWarsSession
from src.platform.games import GameLaunchOptions


def _context():
    settings = SimpleNamespace(
        platform=SimpleNamespace(sound_enabled=True, master_volume=0.8, fullscreen=False, language="vi"),
        update_game_settings=lambda game_id, values: None,
    )
    return SimpleNamespace(settings=settings)


def test_color_wars_exposes_descriptor():
    game = ColorWarsGame()

    assert game.descriptor.game_id == "color_wars"
    assert "pvbot" in game.descriptor.supported_modes


def test_color_wars_create_session_normalizes_launch_options():
    game = ColorWarsGame()

    session = game.create_session(_context(), GameLaunchOptions(mode="bad", difficulty="bad"))

    assert isinstance(session, ColorWarsSession)
    assert session.launch_options.mode == "pvbot"
    assert session.launch_options.difficulty == "easy"
