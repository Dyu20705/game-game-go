import unittest
from collections import Counter

from game.level_generator import LevelGenerator
from game.models import COLOR_ORDER, DIFFICULTIES
from game.rules import is_victory


class LevelGeneratorTests(unittest.TestCase):
    def test_generated_puzzle_has_correct_color_counts(self):
        difficulty = DIFFICULTIES["normal"]
        level = LevelGenerator(seed=1).generate(difficulty)
        actual = Counter()
        for screw in level.screws:
            actual.update(screw.nuts)
        expected = {color: difficulty.capacity for color in COLOR_ORDER[: difficulty.color_count]}
        self.assertEqual(dict(actual), expected)

    def test_generated_puzzle_is_not_already_solved(self):
        difficulty = DIFFICULTIES["easy"]
        level = LevelGenerator(seed=2).generate(difficulty)
        self.assertFalse(is_victory(level.screws))

    def test_initial_state_is_safe_copy(self):
        difficulty = DIFFICULTIES["easy"]
        level = LevelGenerator(seed=3).generate(difficulty)
        before = level.initial_state
        level.screws[0].nuts.clear()
        self.assertEqual(level.initial_state, before)


if __name__ == "__main__":
    unittest.main()
