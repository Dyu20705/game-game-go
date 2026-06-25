"""Tests for choose difficulty scene."""

import unittest
from unittest.mock import patch

import pygame

from src.games.color_wars.view.choose_diff_scene.scene import draw_choose_diff_scene


class TestChooseDiffScene(unittest.TestCase):
    """Validate key labels and button contract."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_draws_localized_difficulty_and_play_button(self):
        screen = pygame.Surface((1200, 720), pygame.SRCALPHA)
        panel = pygame.Rect(80, 40, 460, 640)
        labels = []
        fonts = {
            "main": pygame.font.SysFont("segoeui", 28, bold=True),
            "body": pygame.font.SysFont("segoeui", 20),
            "button": pygame.font.SysFont("segoeui", 20, bold=True),
        }
        colors = {
            "subtitle": (1, 2, 3),
            "diff_colors": {
                "easy": (1, 2, 3),
                "medium": (3, 4, 5),
                "hard": (5, 6, 7),
            },
        }
        rects = {
            "back_rect": pygame.Rect(100, 60, 42, 42),
            "settings_icon_rect": pygame.Rect(460, 60, 42, 42),
            "slider_rect": pygame.Rect(140, 420, 300, 22),
            "knob_x": 240,
            "play_match_btn": pygame.Rect(150, 530, 280, 56),
            "draw_button": lambda _screen, _rect, label, _color, _font: labels.append(label),
        }
        icons = {
            "back": pygame.Surface((42, 42), pygame.SRCALPHA),
            "settings": pygame.Surface((42, 42), pygame.SRCALPHA),
            "medium": pygame.Surface((140, 140), pygame.SRCALPHA),
        }

        with patch("src.games.color_wars.view.choose_diff_scene.scene.blit_fitted_text") as mock_text:
            draw_choose_diff_scene(screen, panel, fonts, colors, rects, "medium", icons)

        rendered = [call.args[2] for call in mock_text.call_args_list]
        self.assertIn("TRUNG BÌNH", rendered)
        self.assertIn("BẮT ĐẦU", labels)


if __name__ == "__main__":
    unittest.main()
