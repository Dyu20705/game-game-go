"""Tests for settings scene rendering behavior."""

import unittest
from unittest.mock import patch

import pygame

from src.games.color_wars.view.setting_scene.scene import draw_setting_scene


class TestSettingScene(unittest.TestCase):
    """Ensure settings UI only shows active, meaningful elements."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_removed_subtitle_and_hint_text_are_not_rendered(self):
        """Legacy instructional lines should not be rendered anymore."""
        screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
        panel = pygame.Rect(320, 170, 640, 380)
        apply_btn = pygame.Rect(560, 460, 180, 40)
        controls = {
            "show_back": True,
            "sound_checkbox": pygame.Rect(780, 338, 24, 24),
            "volume_slider": pygame.Rect(440, 340, 300, 16),
            "volume_knob_x": 590,
            "sound_enabled": True,
            "sound_volume": 0.5,
            "apply_btn": apply_btn,
        }
        colors = {"btn_slate": (120, 120, 120)}
        fonts = {
            "main": pygame.font.SysFont("segoeui", 30, bold=True),
            "body": pygame.font.SysFont("segoeui", 20),
        }
        back_rect = pygame.Rect(336, 186, 42, 42)
        back_icon = pygame.Surface((42, 42), pygame.SRCALPHA)

        with patch("src.games.color_wars.view.setting_scene.scene.blit_fitted_text") as mock_text:
            draw_setting_scene(screen, panel, fonts, colors, back_rect, back_icon, controls)

        rendered = [call.args[2] for call in mock_text.call_args_list]
        self.assertIn("Cài đặt trận đấu", rendered)
        self.assertNotIn("Âm thanh và tùy chọn trận đấu", rendered)
        self.assertNotIn("Nhấn Áp dụng để lưu thay đổi.", rendered)

    def test_no_apply_side_checkmark_is_drawn(self):
        """Decorative checkmark to the right of Apply should stay removed."""
        screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
        panel = pygame.Rect(320, 170, 640, 380)
        apply_btn = pygame.Rect(560, 460, 180, 40)
        controls = {
            "show_back": True,
            "sound_checkbox": pygame.Rect(780, 338, 24, 24),
            "volume_slider": pygame.Rect(440, 340, 300, 16),
            "volume_knob_x": 590,
            "sound_enabled": True,
            "sound_volume": 0.5,
            "apply_btn": apply_btn,
        }
        colors = {"btn_slate": (120, 120, 120)}
        fonts = {
            "main": pygame.font.SysFont("segoeui", 30, bold=True),
            "body": pygame.font.SysFont("segoeui", 20),
        }
        back_rect = pygame.Rect(336, 186, 42, 42)
        back_icon = pygame.Surface((42, 42), pygame.SRCALPHA)
        removed_mark_center = (apply_btn.right + 18, apply_btn.centery)

        with patch("src.games.color_wars.view.setting_scene.scene.pygame.draw.circle") as mock_circle:
            draw_setting_scene(screen, panel, fonts, colors, back_rect, back_icon, controls)

        drawn_centers = [call.args[2] for call in mock_circle.call_args_list if len(call.args) >= 3]
        self.assertNotIn(removed_mark_center, drawn_centers)


if __name__ == "__main__":
    unittest.main()
