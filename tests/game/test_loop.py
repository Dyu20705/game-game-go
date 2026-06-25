"""Tests for gameplay runtime loop guards."""

import unittest

from src.games.color_wars.runtime.loop import run_game


class TestRunGame(unittest.TestCase):
    """Validate loop argument checking and early guards."""

    def test_invalid_core_type_raises_type_error(self):
        with self.assertRaises(TypeError):
            run_game(core=object())


if __name__ == "__main__":
    unittest.main()
