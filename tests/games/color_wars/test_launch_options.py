from src.games.color_wars.game import ColorWarsGame
from src.platform.games import GameLaunchOptions


def test_color_wars_accepts_pvp_and_hard_options():
    class Settings:
        platform = None

        def update_game_settings(self, game_id, values):
            self.values = values

    context = type("Context", (), {"settings": Settings()})()

    session = ColorWarsGame().create_session(context, GameLaunchOptions(mode="pvp", difficulty="hard"))

    assert session.launch_options.mode == "pvp"
    assert session.launch_options.difficulty == "hard"

