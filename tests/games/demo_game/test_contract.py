from src.games.demo_game.game import DemoGame, DemoGameSession
from src.platform.games import GameLaunchOptions


def test_demo_game_exposes_descriptor():
    game = DemoGame()

    assert game.descriptor.game_id == "demo_game"
    assert game.descriptor.enabled is True


def test_demo_game_creates_session():
    session = DemoGame().create_session(object(), GameLaunchOptions())

    assert isinstance(session, DemoGameSession)
