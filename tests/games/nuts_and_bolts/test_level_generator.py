from collections import Counter

from src.games.nuts_and_bolts.level_generator import LevelGenerator
from src.games.nuts_and_bolts.models import COLOR_ORDER, DIFFICULTIES
from src.games.nuts_and_bolts.rules import is_victory


def test_generated_puzzle_has_correct_color_counts():
    difficulty = DIFFICULTIES["normal"]
    level = LevelGenerator(seed=1).generate(difficulty)
    actual = Counter()
    for screw in level.screws:
        actual.update(screw.nuts)
    expected = {color: difficulty.capacity for color in COLOR_ORDER[: difficulty.color_count]}
    assert dict(actual) == expected


def test_generated_puzzle_is_not_already_solved():
    difficulty = DIFFICULTIES["easy"]
    level = LevelGenerator(seed=2).generate(difficulty)
    assert not is_victory(level.screws)


def test_initial_state_is_safe_copy():
    difficulty = DIFFICULTIES["easy"]
    level = LevelGenerator(seed=3).generate(difficulty)
    before = level.initial_state
    level.screws[0].nuts.clear()
    assert level.initial_state == before
