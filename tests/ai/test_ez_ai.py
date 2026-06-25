"""Tests for easy AI behavior."""

import unittest
from unittest.mock import patch

from src.games.color_wars.ai.ez_AI import get_ez_move


class TestEasyAI(unittest.TestCase):
    """Validate easy AI move selection policy."""

    def test_returns_none_when_no_valid_moves(self):
        board = [[1, 1], [1, 1]]
        dots = [[1, 2], [2, 1]]

        self.assertIsNone(get_ez_move(board, dots))

    def test_prefers_weaker_pool_when_probability_hits(self):
        board = [[0, 0], [0, 0]]
        dots = [[0, 0], [0, 0]]

        with (
            patch("src.games.color_wars.ai.ez_AI.random.random", return_value=0.0),
            patch(
                "src.games.color_wars.ai.ez_AI._worst_half_moves",
                return_value=[(1, 0)],
            ) as weak_mock,
            patch("src.games.color_wars.ai.ez_AI.random.choice", return_value=(1, 0)) as choice_mock,
        ):
            move = get_ez_move(board, dots)

        self.assertEqual(move, (1, 0))
        weak_mock.assert_called_once()
        choice_mock.assert_called_once_with([(1, 0)])

    def test_falls_back_to_any_valid_move(self):
        board = [[0, 0], [0, 0]]
        dots = [[0, 0], [0, 0]]

        with (
            patch("src.games.color_wars.ai.ez_AI.random.random", return_value=0.99),
            patch(
                "src.games.color_wars.ai.ez_AI.random.choice",
                side_effect=lambda seq: seq[0],
            ),
        ):
            move = get_ez_move(board, dots)

        self.assertIn(move, {(0, 0), (0, 1), (1, 0), (1, 1)})


if __name__ == "__main__":
    unittest.main()
