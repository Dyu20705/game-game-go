"""Tests for tutorial overlay sizing and visibility constraints."""

import unittest

import pygame

from src.games.color_wars.view.commons.tutorial_overlay import draw_tutorial_overlay


class TestTutorialOverlay(unittest.TestCase):
    """Ensure tutorial overlay is large enough to display content reliably."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.font.init()

    @classmethod
    def tearDownClass(cls):
        pygame.font.quit()
        pygame.quit()

    def test_overlay_uses_large_screen_relative_size(self):
        """Overlay should scale to a large area instead of narrow panel width."""
        screen = pygame.Surface((1280, 720), pygame.SRCALPHA)
        panel = pygame.Rect(48, 36, 420, 648)
        fonts = {
            "main": pygame.font.SysFont("segoeui", 30, bold=True),
            "body": pygame.font.SysFont("segoeui", 20),
        }
        colors = {}
        lines = [
            "Giới thiệu",
            "Luật chơi",
            "Nổ dây chuyền",
            "Mẹo chơi",
            "Phím tắt",
        ]

        rects = draw_tutorial_overlay(screen, panel, fonts, colors, lines, close_label="Đóng")
        overlay = rects["overlay"]

        self.assertGreaterEqual(overlay.width, int(screen.get_width() * 0.78))
        self.assertGreaterEqual(overlay.height, int(screen.get_height() * 0.82))


if __name__ == "__main__":
    unittest.main()
