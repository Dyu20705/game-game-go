"""Test core game rules engine."""

import unittest

from src.games.color_wars.engine.rules import (
    EMPTY,
    PLAYER_BLUE,
    get_capacity,
    get_move_dot_increment,
    get_valid_moves,
)


class TestRules(unittest.TestCase):
    """Validate move legality and dot increment logic."""

    def test_get_capacity_is_fixed_4_everywhere(self):
        """Every cell has fixed capacity of 4 dots."""
        size = 5
        self.assertEqual(get_capacity(0, 0, size), 4)
        self.assertEqual(get_capacity(0, 2, size), 4)
        self.assertEqual(get_capacity(2, 2, size), 4)
        self.assertEqual(get_capacity(4, 4, size), 4)

    def test_valid_moves_first_turn_only_empty_cells(self):
        """First move must be on empty cells."""
        board = [
            [EMPTY, 2, EMPTY],
            [2, 2, EMPTY],
            [EMPTY, 2, EMPTY],
        ]

        moves = set(get_valid_moves(board, PLAYER_BLUE))
        expected = {(0, 0), (0, 2), (1, 2), (2, 0), (2, 2)}

        self.assertSetEqual(moves, expected)

    def test_valid_moves_after_init_only_own_cells(self):
        """After initial placement, can only reinforce own cells."""
        board = [
            [EMPTY, PLAYER_BLUE, 2],
            [2, EMPTY, PLAYER_BLUE],
            [2, 2, EMPTY],
        ]

        moves = set(get_valid_moves(board, PLAYER_BLUE))
        expected = {(0, 1), (1, 2)}

        self.assertSetEqual(moves, expected)

    def test_move_dot_increment_is_3_for_empty_and_1_for_owned(self):
        """Empty capture: +3 dots. Reinforce: +1 dot."""
        board = [
            [EMPTY, PLAYER_BLUE],
            [2, EMPTY],
        ]

        self.assertEqual(get_move_dot_increment(board, 0, 0), 3)
        self.assertEqual(get_move_dot_increment(board, 0, 1), 1)


if __name__ == "__main__":
    unittest.main()
