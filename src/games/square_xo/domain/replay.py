"""Canonical serialization, hashing, and replay for SquareXO."""

import hashlib
import json

from src.platform.blockchain.domain.result import CanonicalMatchResult, CanonicalMove, MatchEnvelope

from .board import create_game
from .move import ClaimEdge
from .result import result_from_state
from .rules import apply_move
from .state import Edge, Player, Point, SquareXOState

RULESET_VERSION = "square_xo.port.v1"


def state_to_dict(state: SquareXOState) -> dict[str, object]:
    return {
        "rows": state.rows,
        "cols": state.cols,
        "edges": [
            {
                "from": {"row": edge.from_point.row, "col": edge.from_point.col},
                "to": {"row": edge.to_point.row, "col": edge.to_point.col},
                "takenBy": edge.taken_by.value if edge.taken_by else None,
            }
            for edge in state.edges
        ],
        "boxes": [{"row": box.row, "col": box.col, "owner": box.owner.value} for box in state.boxes],
        "currentPlayer": state.current_player.value,
        "score": state.score,
    }


def state_from_dict(data: dict[str, object]) -> SquareXOState:
    edges = tuple(
        Edge(
            Point(int(item["from"]["row"]), int(item["from"]["col"])),
            Point(int(item["to"]["row"]), int(item["to"]["col"])),
            Player(item["takenBy"]) if item.get("takenBy") else None,
        )
        for item in data["edges"]
    )
    from .state import BoxClaim

    boxes = tuple(BoxClaim(int(item["row"]), int(item["col"]), Player(item["owner"])) for item in data.get("boxes", []))
    score = data.get("score", {})
    return SquareXOState(
        rows=int(data["rows"]),
        cols=int(data["cols"]),
        edges=edges,
        boxes=boxes,
        current_player=Player(data["currentPlayer"]),
        score_x=int(score.get("X", 0)),
        score_o=int(score.get("O", 0)),
    )


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def state_hash(state: SquareXOState) -> str:
    return hashlib.sha256(canonical_json(state_to_dict(state)).encode("utf-8")).hexdigest()


def move_to_canonical(move: ClaimEdge) -> CanonicalMove:
    return CanonicalMove(
        "claim_edge",
        {
            "player": move.player.value,
            "from": {"row": move.edge.from_point.row, "col": move.edge.from_point.col},
            "to": {"row": move.edge.to_point.row, "col": move.edge.to_point.col},
        },
    )


def move_from_canonical(move: CanonicalMove) -> ClaimEdge:
    payload = move.payload
    return ClaimEdge(
        Edge(
            Point(int(payload["from"]["row"]), int(payload["from"]["col"])),
            Point(int(payload["to"]["row"]), int(payload["to"]["col"])),
        ),
        Player(payload["player"]),
    )


def apply_replay(rows: int, cols: int, moves: tuple[CanonicalMove, ...]) -> SquareXOState:
    state = create_game(rows, cols)
    for move in moves:
        state = apply_move(state, move_from_canonical(move))
    return state


def envelope_for_replay(match_id: str, initial: SquareXOState, moves: tuple[ClaimEdge, ...]) -> MatchEnvelope:
    state = initial
    canonical_moves = []
    for move in moves:
        canonical = move_to_canonical(move)
        canonical_moves.append(canonical)
        state = apply_move(state, move)
    result = result_from_state(state)
    return MatchEnvelope(
        protocol_version="1",
        game_id="square_xo",
        ruleset_version=RULESET_VERSION,
        match_id=match_id,
        players=("X", "O"),
        initial_state_hash=state_hash(initial),
        moves=tuple(canonical_moves),
        final_state_hash=state_hash(state),
        result=CanonicalMatchResult(winner=result.winner, scores=result.scores, terminal_reason=result.reason),
        metadata={"rows": initial.rows, "cols": initial.cols},
    )
