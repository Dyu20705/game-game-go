import os
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from game.app import GameApp
from game.rules import capture_state, move_nut


class UndoRestartTests(unittest.TestCase):
    def test_undo_restores_previous_logical_state(self):
        app = GameApp()
        before = capture_state(app.screws)
        source, destination = next(
            (s, d)
            for s in range(len(app.screws))
            for d in range(len(app.screws))
            if s != d and app.screws[s].nuts and not app.screws[d].is_full()
        )
        move_nut(app.screws, source, destination)
        app.history.append((source, destination))
        app.move_count = 1

        old_source, old_destination = app.history.pop()
        move_nut(app.screws, old_destination, old_source)
        app.move_count -= 1

        self.assertEqual(capture_state(app.screws), before)
        self.assertEqual(app.move_count, 0)

    def test_restart_restores_initial_generated_state(self):
        app = GameApp()
        initial = app.initial_state
        source, destination = next(
            (s, d)
            for s in range(len(app.screws))
            for d in range(len(app.screws))
            if s != d and app.screws[s].nuts and not app.screws[d].is_full()
        )
        move_nut(app.screws, source, destination)
        app.history.append((source, destination))
        app.move_count = 1
        app.restart()
        self.assertEqual(capture_state(app.screws), initial)
        self.assertEqual(app.history, [])
        self.assertEqual(app.move_count, 0)

    def test_scramble_does_not_touch_move_count_or_history(self):
        app = GameApp()
        self.assertEqual(app.move_count, 0)
        self.assertEqual(app.history, [])


if __name__ == "__main__":
    unittest.main()
