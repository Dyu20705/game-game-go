"""Test home menu scene and difficulty selection."""

import unittest

import pygame

from src.games.color_wars.view.home_scene import compute_menu_icon_rects, difficulty_from_percent
from src.games.color_wars.view.home_scene.scene import draw_home_scene


class TestHomeScene(unittest.TestCase):
    """Home menu UI layout and controls."""

    def test_menu_icons_are_inside_panel_header(self):
        """Tutorial/settings icons stay inside panel and aligned on top-right."""
        panel = pygame.Rect(100, 80, 600, 420)
        tutorial_rect, settings_rect = compute_menu_icon_rects(panel)

        self.assertEqual(tutorial_rect.y, settings_rect.y)
        self.assertLess(tutorial_rect.x, settings_rect.x)
        self.assertEqual(settings_rect.x - tutorial_rect.x, tutorial_rect.width + 8)
        self.assertGreaterEqual(tutorial_rect.left, panel.left)
        self.assertLessEqual(settings_rect.right, panel.right)
        self.assertGreaterEqual(settings_rect.top, panel.top)

    def test_difficulty_from_percent_easy(self):
        """Low percent maps to Easy."""
        self.assertEqual(difficulty_from_percent(0.0), "easy")
        self.assertEqual(difficulty_from_percent(0.2), "easy")

    def test_difficulty_from_percent_medium(self):
        """Mid percent maps to Medium."""
        self.assertEqual(difficulty_from_percent(0.5), "medium")

    def test_difficulty_from_percent_hard(self):
        """High percent maps to Hard."""
        self.assertEqual(difficulty_from_percent(0.9), "hard")

    def test_difficulty_from_percent_clamps_bounds(self):
        """Handles out-of-range input safely."""
        self.assertEqual(difficulty_from_percent(-1), "easy")
        self.assertEqual(difficulty_from_percent(2), "hard")

    def test_home_scene_buttons_use_vietnamese_labels(self):
        """Home scene draws the expected Play/Quit labels."""
        labels = []

        def fake_draw_button(_screen, _rect, label, _color, _font):
            labels.append(label)

        rects = {
            "draw_button": fake_draw_button,
            "play_btn": pygame.Rect(0, 0, 100, 40),
            "quit_btn": pygame.Rect(0, 50, 100, 40),
        }

        draw_home_scene(
            None, pygame.Rect(0, 0, 300, 200), {"button": None}, {"btn_green": (0, 0, 0), "btn_red": (0, 0, 0)}, rects
        )
        self.assertEqual(labels, ["BẮT ĐẦU", "THOÁT"])


if __name__ == "__main__":
    unittest.main()
