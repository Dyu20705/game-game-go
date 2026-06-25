"""Tests for gameplay board/effects/scene rendering contracts."""

import unittest
from unittest.mock import patch

import pygame

from src.games.color_wars.engine.rules import PLAYER_BLUE
from src.games.color_wars.runtime.state import GameState
from src.games.color_wars.view.gameplay_scene.board import drawDot
from src.games.color_wars.view.gameplay_scene.effects import drawExplosionOverlay
from src.games.color_wars.view.gameplay_scene.scene import draw_gameplay_scene


class TestGameplayViewContracts(unittest.TestCase):
    """Validate core render helper behavior with lightweight assertions."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_draw_dot_uses_expected_circle_count(self):
        screen = pygame.Surface((320, 320), pygame.SRCALPHA)

        with patch("src.games.color_wars.view.gameplay_scene.board.pygame.draw.circle") as circle_mock:
            drawDot(screen, 20, 20, 1, (255, 255, 255), 60)
            drawDot(screen, 20, 20, 2, (255, 255, 255), 60)
            drawDot(screen, 20, 20, 3, (255, 255, 255), 60)
            drawDot(screen, 20, 20, 4, (255, 255, 255), 60)

        self.assertEqual(circle_mock.call_count, 10)

    def test_draw_explosion_overlay_ignores_invalid_step(self):
        screen = pygame.Surface((400, 400), pygame.SRCALPHA)
        layout = {
            "board_x": 50,
            "board_y": 50,
            "cell_size": 60,
            "width": 400,
            "height": 400,
        }

        drawExplosionOverlay(screen, layout, None, 0.5)
        drawExplosionOverlay(screen, layout, {"center": None, "targets": [], "owner": PLAYER_BLUE}, 0.5)

    def test_draw_gameplay_scene_uses_turn_background(self):
        state = GameState()
        board = state.board
        dots = state.dots

        class FakeScreen:
            def __init__(self):
                self.filled = False

            def get_size(self):
                return (1280, 720)

            def fill(self, _color):
                self.filled = True

        screen = FakeScreen()

        with (
            patch(
                "src.games.color_wars.view.gameplay_scene.scene.drawBoard",
            ) as board_mock,
            patch(
                "src.games.color_wars.view.gameplay_scene.scene.drawHud",
            ) as hud_mock,
        ):
            draw_gameplay_scene(
                screen,
                state,
                board,
                dots,
                state.current_player,
                0,
                0,
                None,
                "pvbot",
                "easy",
            )

        self.assertTrue(screen.filled)
        board_mock.assert_called_once()
        hud_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
