"""Tests for choose game mode scene rendering contract."""

import unittest
from unittest.mock import patch

import pygame

from src.games.color_wars.view.choose_gamemode_scene.scene import draw_choose_gamemode_scene


class TestChooseGameModeScene(unittest.TestCase):
    """Validate key text and scene structure in choose-mode view."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_draws_choose_mode_title(self):
        """Scene should render the requested heading text."""
        screen = pygame.Surface((1200, 720))
        panel = pygame.Rect(60, 40, 420, 640)
        fonts = {
            "main": pygame.font.SysFont("segoeui", 28, bold=True),
            "button": pygame.font.SysFont("segoeui", 18, bold=True),
        }
        colors = {
            "title": (255, 255, 255),
            "btn_blue": (50, 120, 200),
            "btn_green": (80, 160, 120),
        }
        rects = {
            "back_rect": pygame.Rect(80, 60, 42, 42),
            "settings_icon_rect": pygame.Rect(400, 60, 42, 42),
            "pvp_btn": pygame.Rect(120, 300, 300, 52),
            "pvbot_btn": pygame.Rect(120, 368, 300, 52),
        }

        icon_surface = pygame.Surface((42, 42), pygame.SRCALPHA)
        mode_icon = pygame.Surface((52, 52), pygame.SRCALPHA)
        icons = {
            "back": icon_surface,
            "settings": icon_surface,
            "mode_pvp": mode_icon,
            "mode_pvbot": mode_icon,
        }

        with patch("src.games.color_wars.view.choose_gamemode_scene.scene.blit_fitted_text") as mock_text:
            draw_choose_gamemode_scene(screen, panel, fonts, colors, rects, icons)

        rendered_texts = [call.args[2] for call in mock_text.call_args_list]
        self.assertIn("Chọn chế độ chơi", rendered_texts)


if __name__ == "__main__":
    unittest.main()
