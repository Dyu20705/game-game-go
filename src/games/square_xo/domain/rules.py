"""SquareXO deterministic rules ported from the TypeScript game-core."""

from dataclasses import replace

from .board import edge_key
from .move import ClaimEdge
from .state import BoxClaim, Edge, Player, SquareXOState


def square_edge_keys(row: int, col: int) -> tuple[str, str, str, str]:
    top = f"{row},{col}-{row},{col + 1}"
    bottom = f"{row + 1},{col}-{row + 1},{col + 1}"
    left = f"{row},{col}-{row + 1},{col}"
    right = f"{row},{col + 1}-{row + 1},{col + 1}"
    return top, right, bottom, left


def completed_square_positions(state: SquareXOState, taken_edge_keys: set[str]) -> list[tuple[int, int]]:
    completed = []
    for row in range(state.rows):
        for col in range(state.cols):
            if all(key in taken_edge_keys for key in square_edge_keys(row, col)):
                completed.append((row, col))
    return completed


def apply_move(state: SquareXOState, move: ClaimEdge) -> SquareXOState:
    if state.is_terminal:
        raise ValueError("Game is already terminal")
    if move.player != state.current_player:
        raise ValueError("Only the current player can move")

    move_key = edge_key(move.edge)
    target_index = next((index for index, edge in enumerate(state.edges) if edge_key(edge) == move_key), -1)
    if target_index == -1:
        raise ValueError("Invalid edge for this board")
    if state.edges[target_index].taken_by is not None:
        raise ValueError("Edge already taken")

    taken_before = {edge_key(edge) for edge in state.edges if edge.taken_by is not None}
    completed_before = completed_square_positions(state, taken_before)
    new_edges = tuple(
        replace(edge, taken_by=move.player) if index == target_index else edge
        for index, edge in enumerate(state.edges)
    )
    taken_after = set(taken_before)
    taken_after.add(move_key)
    completed_after = completed_square_positions(state, taken_after)
    claimed_before = {(box.row, box.col) for box in state.boxes}
    new_claims = tuple(
        BoxClaim(row=row, col=col, owner=move.player)
        for row, col in completed_after
        if (row, col) not in claimed_before
    )
    newly_completed = len(completed_after) - len(completed_before)
    return SquareXOState(
        rows=state.rows,
        cols=state.cols,
        edges=new_edges,
        boxes=state.boxes + new_claims,
        current_player=move.player if newly_completed > 0 else move.player.next(),
        score_x=state.score_x + (newly_completed if move.player == Player.X else 0),
        score_o=state.score_o + (newly_completed if move.player == Player.O else 0),
    )

