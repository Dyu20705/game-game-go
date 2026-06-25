import unittest

from game.models import Screw
from game.rules import can_move, capture_state, is_completed_screw, is_victory, move_nut


class RuleTests(unittest.TestCase):
    def test_can_move_from_non_empty_to_non_full(self):
        screws = [Screw("red", 2, ["red"]), Screw(None, 2, [])]
        self.assertTrue(can_move(screws, 0, 1))

    def test_cannot_move_from_empty_screw(self):
        screws = [Screw("red", 2, []), Screw(None, 2, [])]
        self.assertFalse(can_move(screws, 0, 1))

    def test_cannot_move_to_full_screw(self):
        screws = [Screw("red", 2, ["red"]), Screw(None, 1, ["blue"])]
        self.assertFalse(can_move(screws, 0, 1))

    def test_only_top_nut_moves(self):
        screws = [Screw("red", 3, ["red", "blue"]), Screw(None, 3, [])]
        moved = move_nut(screws, 0, 1)
        self.assertEqual(moved, "blue")
        self.assertEqual(screws[0].nuts, ["red"])
        self.assertEqual(screws[1].nuts, ["blue"])

    def test_completed_target_screw_detected(self):
        self.assertTrue(is_completed_screw(Screw("green", 2, ["green", "green"])))
        self.assertFalse(is_completed_screw(Screw("green", 2, ["green", "red"])))

    def test_spare_with_nut_prevents_victory(self):
        screws = [Screw("red", 1, ["red"]), Screw(None, 1, ["blue"])]
        self.assertFalse(is_victory(screws))

    def test_completed_targets_and_empty_spares_win(self):
        screws = [
            Screw("red", 1, ["red"]),
            Screw("blue", 1, ["blue"]),
            Screw(None, 1, []),
        ]
        self.assertTrue(is_victory(screws))

    def test_completed_screw_is_locked_as_source(self):
        screws = [Screw("red", 1, ["red"]), Screw(None, 1, [])]
        self.assertFalse(can_move(screws, 0, 1))

    def test_capture_state_is_deep_copy_safe(self):
        screws = [Screw("red", 2, ["red"]), Screw(None, 2, [])]
        state = capture_state(screws)
        screws[0].nuts.append("blue")
        self.assertEqual(state, (("red",), ()))


if __name__ == "__main__":
    unittest.main()
