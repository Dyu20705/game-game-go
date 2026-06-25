"""Tests for medium AI behavior."""

import unittest
from unittest.mock import patch

from src.games.color_wars.ai.med_AI import get_med_move


class TestMediumAI(unittest.TestCase):
    """Validate medium AI move selection branches."""

    def test_returns_none_when_no_moves(self):
        board = [[1, 1], [1, 1]]
        dots = [[1, 1], [1, 1]]

        self.assertIsNone(get_med_move(board, dots))

    def test_uses_tie_noise_between_top_two(self):
        board = [[0]]
        dots = [[0]]

        with (
            patch(
                "src.games.color_wars.ai.med_AI.get_top_moves",
                return_value=[((0, 0), 3.0), ((0, 1), 2.9)],
            ),
            patch(
                "src.games.color_wars.ai.med_AI._response_score",
                side_effect=[1.0, 0.8],
            ),
            patch("src.games.color_wars.ai.med_AI.random.random", return_value=0.99),
            patch(
                "src.games.color_wars.ai.med_AI.random.choice",
                return_value=(0, 1),
            ),
        ):
            move = get_med_move(board, dots)

        self.assertEqual(move, (0, 1))

    def test_can_pick_from_random_pool(self):
        board = [[0]]
        dots = [[0]]

        with (
            patch(
                "src.games.color_wars.ai.med_AI.get_top_moves",
                return_value=[((0, 0), 5.0), ((1, 0), 4.0), ((1, 1), 3.0)],
            ),
            patch(
                "src.games.color_wars.ai.med_AI._response_score",
                side_effect=[4.0, 3.0, 2.0],
            ),
            patch("src.games.color_wars.ai.med_AI.random.random", return_value=0.0),
            patch(
                "src.games.color_wars.ai.med_AI.random.choice",
                return_value=(1, 0),
            ),
        ):
            move = get_med_move(board, dots)

        self.assertEqual(move, (1, 0))


if __name__ == "__main__":
    unittest.main()
