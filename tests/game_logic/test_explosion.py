"""Test explosion chain reaction and ownership conversion."""

import unittest

from src.games.color_wars.engine.explosion import resolve_explosions
from src.games.color_wars.engine.rules import EMPTY, PLAYER_RED


class TestExplosion(unittest.TestCase):
    """Validate chain reaction propagation logic."""

    def test_explosion_happens_at_4_and_assimilates_enemy_cell(self):
        """When dots reach 4, cell explodes and spreads ownership."""
        board = [
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, PLAYER_RED, 1],
            [EMPTY, EMPTY, EMPTY],
        ]
        dots = [
            [0, 0, 0],
            [0, 4, 2],
            [0, 0, 0],
        ]

        resolve_explosions(board, dots, 1, 1)

        self.assertEqual(board[1][1], EMPTY)
        self.assertEqual(dots[1][1], 0)

        self.assertEqual(board[1][2], PLAYER_RED)
        self.assertEqual(dots[1][2], 3)


if __name__ == "__main__":
    unittest.main()
