"""Tests for runtime core systems."""

import unittest
from unittest.mock import MagicMock, patch

from src.games.color_wars.runtime.core import CoreSystems, LaunchConfig, SceneName


class TestCoreSystems(unittest.TestCase):
    """Validate app-level scene and music orchestration."""

    def test_begin_home_session_calls_music_menu_flow(self):
        fake_music = MagicMock()
        with patch("src.games.color_wars.runtime.core.get_music_manager", return_value=fake_music):
            core = CoreSystems()

        core.begin_home_session()

        fake_music.start_new_menu_session.assert_called_once()
        fake_music.enter_menu.assert_called_once()

    def test_enter_gameplay_updates_scene_and_launch(self):
        fake_music = MagicMock()
        with patch("src.games.color_wars.runtime.core.get_music_manager", return_value=fake_music):
            core = CoreSystems()

        launch = LaunchConfig(game_mode="pvp", difficulty="hard")
        core.enter_gameplay(launch)

        self.assertEqual(core.current_scene, SceneName.GAMEPLAY)
        self.assertEqual(core.active_launch, launch)
        fake_music.enter_gameplay.assert_called_once()
        fake_music.apply_audio_preferences.assert_called_once_with(True, 0.75)

    def test_enter_home_and_quit(self):
        fake_music = MagicMock()
        with patch("src.games.color_wars.runtime.core.get_music_manager", return_value=fake_music):
            core = CoreSystems()

        core.enter_home()
        self.assertEqual(core.current_scene, SceneName.HOME)
        fake_music.enter_menu.assert_called_once()

        core.request_quit()
        self.assertEqual(core.current_scene, SceneName.QUIT)


if __name__ == "__main__":
    unittest.main()
