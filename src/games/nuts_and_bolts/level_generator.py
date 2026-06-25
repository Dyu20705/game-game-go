from __future__ import annotations

import random
from collections import Counter
from dataclasses import dataclass

from .models import COLOR_ORDER, Difficulty, Screw, StackState
from .rules import capture_state, is_completed_screw, is_victory, move_nut, valid_moves


@dataclass(frozen=True)
class GeneratedLevel:
    screws: list[Screw]
    initial_state: StackState


class LevelGenerator:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.recent_states: list[StackState] = []

    def generate(self, difficulty: Difficulty, max_attempts: int = 80) -> GeneratedLevel:
        best: list[Screw] | None = None
        for _ in range(max_attempts):
            screws = self._completed_board(difficulty)
            self._scramble(screws, difficulty.scramble_moves)
            if best is None:
                best = [s.copy() for s in screws]
            if self._is_good_puzzle(screws, difficulty):
                state = capture_state(screws)
                self._remember(state)
                return GeneratedLevel(screws, state)

        assert best is not None
        state = capture_state(best)
        self._remember(state)
        return GeneratedLevel(best, state)

    def _completed_board(self, difficulty: Difficulty) -> list[Screw]:
        colors = COLOR_ORDER[: difficulty.color_count]
        screws = [Screw(color, difficulty.capacity, [color] * difficulty.capacity) for color in colors]
        screws.extend(Screw(None, difficulty.capacity, []) for _ in range(difficulty.spare_count))
        return screws

    def _scramble(self, screws: list[Screw], move_count: int) -> None:
        previous: tuple[int, int] | None = None
        for _ in range(move_count):
            moves = valid_moves(screws, lock_completed=False)
            if previous is not None:
                moves = [move for move in moves if move != previous[::-1]]
            if not moves:
                return
            source_index, destination_index = self.random.choice(moves)
            move_nut(screws, source_index, destination_index)
            previous = (source_index, destination_index)

    def _is_good_puzzle(self, screws: list[Screw], difficulty: Difficulty) -> bool:
        state = capture_state(screws)
        if is_victory(screws) or state in self.recent_states:
            return False

        completed = sum(1 for screw in screws if is_completed_screw(screw))
        if completed > max(0, difficulty.color_count - 2):
            return False

        mixed_stacks = sum(1 for screw in screws if len(set(screw.nuts)) > 1)
        if mixed_stacks < max(2, difficulty.color_count // 2):
            return False

        filled_spares = sum(1 for screw in screws if screw.target_color is None and screw.nuts)
        if difficulty.spare_count and filled_spares == 0:
            return False

        return self._has_expected_counts(screws, difficulty)

    @staticmethod
    def _has_expected_counts(screws: list[Screw], difficulty: Difficulty) -> bool:
        expected = {color: difficulty.capacity for color in COLOR_ORDER[: difficulty.color_count]}
        actual: Counter[str] = Counter()
        for screw in screws:
            actual.update(screw.nuts)
        return dict(actual) == expected

    def _remember(self, state: StackState) -> None:
        self.recent_states.append(state)
        self.recent_states = self.recent_states[-12:]
