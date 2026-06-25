"""Test AI mode routing."""

import unittest
from unittest.mock import patch

from src.games.color_wars.ai.ai import get_ai_move


class TestAI(unittest.TestCase):
    """Routes to correct difficulty level."""

    def test_mode_ez_selects_ez_ai(self):
        board = [[0]]
        dots = [[0]]

        with (
            patch("src.games.color_wars.ai.ai.get_ez_move", return_value=(0, 0)) as ez_mock,
            patch("src.games.color_wars.ai.ai.get_med_move", return_value=(1, 1)) as med_mock,
        ):
            move = get_ai_move(board, dots, "ez")

        self.assertEqual(move, (0, 0))
        ez_mock.assert_called_once_with(board, dots)
        med_mock.assert_not_called()

    def test_mode_med_selects_med_ai(self):
        board = [[0]]
        dots = [[0]]

        with (
            patch("src.games.color_wars.ai.ai.get_ez_move", return_value=(0, 0)) as ez_mock,
            patch("src.games.color_wars.ai.ai.get_med_move", return_value=(1, 1)) as med_mock,
        ):
            move = get_ai_move(board, dots, "med")

        self.assertEqual(move, (1, 1))
        med_mock.assert_called_once_with(board, dots)
        ez_mock.assert_not_called()

    def test_mode_hard_selects_hard_ai(self):
        board = [[0]]
        dots = [[0]]

        with patch("src.games.color_wars.ai.ai.get_hard_move", return_value=(2, 2)) as hard_mock:
            move = get_ai_move(board, dots, "hard")

        self.assertEqual(move, (2, 2))
        hard_mock.assert_called_once_with(board, dots)


if __name__ == "__main__":
    unittest.main()
