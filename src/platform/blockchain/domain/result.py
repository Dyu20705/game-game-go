"""Canonical result verification types."""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Mapping


@dataclass(frozen=True)
class CanonicalMove:
    move_type: str
    payload: Mapping[str, object]


@dataclass(frozen=True)
class CanonicalMatchResult:
    winner: str | None
    scores: Mapping[str, int]
    terminal_reason: str


@dataclass(frozen=True)
class MatchEnvelope:
    protocol_version: str
    game_id: str
    ruleset_version: str
    match_id: str
    players: tuple[str, ...]
    initial_state_hash: str
    moves: tuple[CanonicalMove, ...]
    final_state_hash: str
    result: CanonicalMatchResult
    metadata: Mapping[str, object] = field(default_factory=dict)

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "protocol_version": self.protocol_version,
            "game_id": self.game_id,
            "ruleset_version": self.ruleset_version,
            "match_id": self.match_id,
            "players": list(self.players),
            "initial_state_hash": self.initial_state_hash,
            "moves": [{"move_type": move.move_type, "payload": dict(move.payload)} for move in self.moves],
            "final_state_hash": self.final_state_hash,
            "result": {
                "winner": self.result.winner,
                "scores": dict(self.result.scores),
                "terminal_reason": self.result.terminal_reason,
            },
            "metadata": dict(self.metadata),
        }

    def digest(self) -> str:
        encoded = json.dumps(self.to_canonical_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class ReplayVerificationRequest:
    envelope: MatchEnvelope


@dataclass(frozen=True)
class VerificationResult:
    accepted: bool
    result_hash: str | None = None
    reason: str | None = None
