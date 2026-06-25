"""Test Hard AI evaluation and decision making."""

import unittest

from src.games.color_wars.ai.hard_AI import get_hard_move
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED, get_valid_moves


class TestHardAI(unittest.TestCase):
    """Hard AI should make strong strategic decisions."""

    def test_hard_ai_returns_none_when_no_valid_moves(self):
        board = [
            [1, 1],
            [1, 1],
        ]
        dots = [
            [1, 2],
            [2, 1],
        ]

        self.assertIsNone(get_hard_move(board, dots))

    def test_hard_ai_returns_valid_move(self):
        board = [
            [0, 0, 0],
            [0, PLAYER_RED, 0],
            [0, 0, 0],
        ]
        dots = [
            [0, 0, 0],
            [0, 1, 0],
            [0, 0, 0],
        ]

        move = get_hard_move(board, dots)
        valid_moves = set(get_valid_moves(board, PLAYER_RED))

        self.assertIn(move, valid_moves)

    def test_hard_ai_prefers_immediate_gain_when_choice_is_clear(self):
        board = [
            [PLAYER_RED, 0],
            [0, PLAYER_BLUE],
        ]
        dots = [
            [3, 0],
            [0, 1],
        ]

        self.assertEqual(get_hard_move(board, dots), (0, 0))


if __name__ == "__main__":
    unittest.main()
