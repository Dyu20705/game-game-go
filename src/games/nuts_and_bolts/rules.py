from __future__ import annotations

from .models import Screw, StackState


def clone_screws(screws: list[Screw]) -> list[Screw]:
    return [screw.copy() for screw in screws]


def capture_state(screws: list[Screw]) -> StackState:
    return tuple(tuple(screw.nuts) for screw in screws)


def restore_state(screws: list[Screw], state: StackState) -> None:
    for screw, stack in zip(screws, state):
        screw.nuts = list(stack)


def is_completed_screw(screw: Screw) -> bool:
    return (
        screw.target_color is not None
        and len(screw.nuts) == screw.capacity
        and all(nut == screw.target_color for nut in screw.nuts)
    )


def can_move(
    screws: list[Screw],
    source_index: int,
    destination_index: int,
    *,
    lock_completed: bool = True,
) -> bool:
    if source_index == destination_index:
        return False
    if not 0 <= source_index < len(screws):
        return False
    if not 0 <= destination_index < len(screws):
        return False

    source = screws[source_index]
    destination = screws[destination_index]
    if source.is_empty() or destination.is_full():
        return False
    if lock_completed and is_completed_screw(source):
        return False
    return True


def move_nut(screws: list[Screw], source_index: int, destination_index: int) -> str:
    nut = screws[source_index].nuts.pop()
    screws[destination_index].nuts.append(nut)
    return nut


def valid_moves(screws: list[Screw], *, lock_completed: bool = True) -> list[tuple[int, int]]:
    moves: list[tuple[int, int]] = []
    for source_index in range(len(screws)):
        for destination_index in range(len(screws)):
            if can_move(
                screws,
                source_index,
                destination_index,
                lock_completed=lock_completed,
            ):
                moves.append((source_index, destination_index))
    return moves


def is_victory(screws: list[Screw]) -> bool:
    for screw in screws:
        if screw.target_color is None:
            if screw.nuts:
                return False
            continue
        if not is_completed_screw(screw):
            return False
    return True
