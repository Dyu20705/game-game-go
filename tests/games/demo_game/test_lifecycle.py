from src.games.demo_game.game import DemoGameSession
from src.platform.games import GameLaunchOptions


def test_demo_game_random_target_stays_inside_screen():
    class Screen:
        def get_size(self):
            return (640, 480)

    target = DemoGameSession(object(), GameLaunchOptions())._random_target(Screen(), 20)

    assert 40 <= target[0] <= 600
    assert 110 <= target[1] <= 440
