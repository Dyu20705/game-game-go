"""SquareXO result helpers."""

from dataclasses import dataclass

from .state import SquareXOState


@dataclass(frozen=True)
class SquareXOResult:
    winner: str | None
    scores: dict[str, int]
    terminal: bool
    reason: str


def result_from_state(state: SquareXOState) -> SquareXOResult:
    winner = state.winner.value if state.winner else None
    reason = "complete" if state.is_terminal else "in_progress"
    if state.is_terminal and winner is None:
        reason = "draw"
    return SquareXOResult(winner=winner, scores=state.score, terminal=state.is_terminal, reason=reason)
