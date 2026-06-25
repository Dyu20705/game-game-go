"""Tests for game state dataclass."""

import unittest

from src.games.color_wars.engine.rules import EMPTY, PLAYER_BLUE
from src.games.color_wars.runtime.state import GameState


class TestGameState(unittest.TestCase):
    """Validate default game state values."""

    def test_initial_state_is_empty_and_blue_turn(self):
        state = GameState()

        self.assertEqual(state.current_player, PLAYER_BLUE)
        self.assertEqual(state.grid_size, 5)
        self.assertEqual(len(state.board), 5)
        self.assertEqual(len(state.dots), 5)
        self.assertTrue(all(cell == EMPTY for row in state.board for cell in row))
        self.assertTrue(all(dot == 0 for row in state.dots for dot in row))


if __name__ == "__main__":
    unittest.main()
