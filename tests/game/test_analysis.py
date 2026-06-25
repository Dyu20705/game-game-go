"""Tests for gameplay analysis helpers."""

import unittest

from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED
from src.games.color_wars.runtime.analysis import estimate_win_chances, format_cell_label
from src.games.color_wars.runtime.state import GameState


class TestAnalysis(unittest.TestCase):
    """Validate stable outputs for chance and coordinate formatting."""

    def test_estimate_win_chances_handles_terminal_state(self):
        state = GameState()
        state.winner = PLAYER_BLUE
        self.assertEqual(estimate_win_chances(state), (100.0, 0.0))

        state.winner = PLAYER_RED
        self.assertEqual(estimate_win_chances(state), (0.0, 100.0))

    def test_estimate_win_chances_returns_valid_probability_range(self):
        state = GameState()
        blue, red = estimate_win_chances(state)

        self.assertGreaterEqual(blue, 0.0)
        self.assertLessEqual(blue, 100.0)
        self.assertEqual(round(blue + red, 1), 100.0)

    def test_format_cell_label(self):
        self.assertEqual(format_cell_label(0, 0), "A1")
        self.assertEqual(format_cell_label(4, 2), "C5")
        self.assertEqual(format_cell_label(None, 2), "-")


if __name__ == "__main__":
    unittest.main()
