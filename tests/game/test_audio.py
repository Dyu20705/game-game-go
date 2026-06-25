"""Tests for music manager behavior."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.games.color_wars.runtime.audio import MusicManager


class TestMusicManager(unittest.TestCase):
    """Validate music manager state transitions without real audio device."""

    def test_start_new_menu_session_selects_theme_once(self):
        manager = MusicManager()
        tracks = [Path("a.mp3"), Path("b.mp3")]

        with (
            patch("src.games.color_wars.runtime.audio._resolve_music_paths", return_value=tracks),
            patch(
                "src.games.color_wars.runtime.audio.pygame.mixer.get_init",
                return_value=True,
            ),
            patch("src.games.color_wars.runtime.audio.pygame.mixer.init"),
            patch("src.games.color_wars.runtime.audio.random.shuffle", lambda seq: None),
        ):
            manager.start_new_menu_session()
            first_theme = manager._theme_track
            manager.start_new_menu_session()

        self.assertEqual(first_theme, tracks[0])
        self.assertEqual(manager._theme_track, tracks[0])

    def test_apply_audio_preferences_pauses_when_disabled(self):
        manager = MusicManager()
        manager._mixer_ready = True
        manager._tracks = [Path("a.mp3")]

        with patch("src.games.color_wars.runtime.audio.pygame.mixer.music") as music:
            manager.apply_audio_preferences(False, 0.3)

        music.set_volume.assert_called_once_with(0.3)
        music.pause.assert_called_once()

    def test_apply_audio_preferences_unpauses_and_replays(self):
        manager = MusicManager()
        manager._mixer_ready = True
        manager._tracks = [Path("a.mp3")]
        manager._active_track = Path("a.mp3")

        with patch("src.games.color_wars.runtime.audio.pygame.mixer.music") as music:
            music.get_busy.return_value = False
            manager.apply_audio_preferences(True, 0.5)

        music.set_volume.assert_called_once_with(0.5)
        music.unpause.assert_called_once()
        music.play.assert_called_once_with(-1)

    def test_enter_gameplay_skips_reload_when_theme_is_active(self):
        manager = MusicManager()
        manager._theme_track = Path("a.mp3")
        manager._active_track = Path("a.mp3")
        manager.apply_audio_preferences = MagicMock()
        manager._load_and_play = MagicMock()

        with patch("src.games.color_wars.runtime.audio.pygame.mixer.music.get_busy", return_value=True):
            manager.enter_gameplay()

        manager._load_and_play.assert_not_called()
        manager.apply_audio_preferences.assert_not_called()


if __name__ == "__main__":
    unittest.main()
