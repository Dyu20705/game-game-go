"""Tests for app-level settings."""

import unittest

from src.games.color_wars.runtime.settings import AppSettings, clamp01


class TestSettings(unittest.TestCase):
    """Validate clamp and mutator semantics."""

    def test_clamp01_limits_range(self):
        self.assertEqual(clamp01(-1.2), 0.0)
        self.assertEqual(clamp01(1.8), 1.0)
        self.assertEqual(clamp01(0.25), 0.25)

    def test_settings_mutators_apply_clamped_values(self):
        settings = AppSettings()
        settings.set_sound_enabled(False)
        settings.set_sound_volume(3)
        settings.set_fullscreen(True)

        self.assertFalse(settings.sound_enabled)
        self.assertEqual(settings.sound_volume, 1.0)
        self.assertTrue(settings.fullscreen)


if __name__ == "__main__":
    unittest.main()
