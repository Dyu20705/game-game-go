"""Tests for shared layout/window and win scene helpers."""

import unittest
from unittest.mock import patch

import pygame

from src.games.color_wars.engine.rules import PLAYER_BLUE
from src.games.color_wars.view.layout import compute_layout, get_cell_from_mouse
from src.games.color_wars.view.win_scene.scene import draw_win_scene, get_win_action_rects
from src.games.color_wars.view.window import toggle_fullscreen


class TestLayoutWindowWinScene(unittest.TestCase):
    """Validate utility-level view behavior."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_layout_and_cell_mapping(self):
        screen = pygame.Surface((1000, 700))
        layout = compute_layout(screen, 5)

        self.assertGreater(layout["board_size"], 0)
        self.assertGreater(layout["cell_size"], 0)

        center_x = int(layout["board_x"] + layout["cell_size"] * 1.5)
        center_y = int(layout["board_y"] + layout["cell_size"] * 2.5)
        self.assertEqual(get_cell_from_mouse((center_x, center_y), 5, screen), (2, 1))
        self.assertEqual(get_cell_from_mouse((0, 0), 5, screen), (None, None))

    def test_toggle_fullscreen_switches_state(self):
        fake_screen = object()
        with patch("src.games.color_wars.view.window.drawScreen", return_value=fake_screen) as draw_mock:
            screen, is_full = toggle_fullscreen(False, None)

        self.assertIs(screen, fake_screen)
        self.assertTrue(is_full)
        draw_mock.assert_called_once_with(fullscreen=True)

    def test_win_scene_returns_action_rects(self):
        screen = pygame.Surface((1280, 720))
        rects = get_win_action_rects(screen)

        self.assertIn("panel", rects)
        self.assertIn("restart_rect", rects)
        self.assertIn("home_rect", rects)

    def test_draw_win_scene_none_winner_returns_empty(self):
        screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
        icons = {}

        self.assertEqual(draw_win_scene(screen, None, icons), {})

    def test_draw_win_scene_blue_returns_clickable_rects(self):
        screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
        rects = draw_win_scene(screen, PLAYER_BLUE, {})

        self.assertIn("restart_rect", rects)
        self.assertIn("home_rect", rects)


if __name__ == "__main__":
    unittest.main()
