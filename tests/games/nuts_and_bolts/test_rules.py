from src.games.nuts_and_bolts.models import Screw
from src.games.nuts_and_bolts.rules import can_move, capture_state, is_completed_screw, is_victory, move_nut


def test_can_move_from_non_empty_to_non_full():
    screws = [Screw("red", 2, ["red"]), Screw(None, 2, [])]
    assert can_move(screws, 0, 1)


def test_cannot_move_from_empty_screw():
    screws = [Screw("red", 2, []), Screw(None, 2, [])]
    assert not can_move(screws, 0, 1)


def test_cannot_move_to_full_screw():
    screws = [Screw("red", 2, ["red"]), Screw(None, 1, ["blue"])]
    assert not can_move(screws, 0, 1)


def test_only_top_nut_moves():
    screws = [Screw("red", 3, ["red", "blue"]), Screw(None, 3, [])]
    moved = move_nut(screws, 0, 1)
    assert moved == "blue"
    assert screws[0].nuts == ["red"]
    assert screws[1].nuts == ["blue"]


def test_completed_target_screw_detected():
    assert is_completed_screw(Screw("green", 2, ["green", "green"]))
    assert not is_completed_screw(Screw("green", 2, ["green", "red"]))


def test_spare_with_nut_prevents_victory():
    screws = [Screw("red", 1, ["red"]), Screw(None, 1, ["blue"])]
    assert not is_victory(screws)


def test_completed_targets_and_empty_spares_win():
    screws = [
        Screw("red", 1, ["red"]),
        Screw("blue", 1, ["blue"]),
        Screw(None, 1, []),
    ]
    assert is_victory(screws)


def test_completed_screw_is_locked_as_source():
    screws = [Screw("red", 1, ["red"]), Screw(None, 1, [])]
    assert not can_move(screws, 0, 1)


def test_capture_state_is_deep_copy_safe():
    screws = [Screw("red", 2, ["red"]), Screw(None, 2, [])]
    state = capture_state(screws)
    screws[0].nuts.append("blue")
    assert state == (("red",), ())
