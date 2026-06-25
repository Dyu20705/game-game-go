"""Test controller state updates and move history tracking."""

import unittest

from src.games.color_wars.controller import apply_move
from src.games.color_wars.engine.rules import PLAYER_BLUE
from src.games.color_wars.runtime.state import GameState


class TestController(unittest.TestCase):
    """Controller move handling."""

    def test_apply_move_tracks_last_move_and_history(self):
        state = GameState()

        moved = apply_move(state, 0, 0, player=PLAYER_BLUE)

        self.assertTrue(moved)
        self.assertEqual(state.last_move, (0, 0))
        self.assertEqual(state.move_history[-1], (PLAYER_BLUE, 0, 0))
        self.assertGreaterEqual(len(state.move_history), 1)


if __name__ == "__main__":
    unittest.main()
