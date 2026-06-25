"""Domain-separated result commitment helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Mapping

from src.platform.blockchain.domain.result import MatchEnvelope

COMMITMENT_DOMAIN = "GGG_RESULT_COMMITMENT_V1"
COMMITMENT_SCHEMA_VERSION = 1
COMMITMENT_HASH_ALGORITHM = "sha256"


@dataclass(frozen=True)
class ResultCommitmentPayload:
    schema_version: int
    domain: str
    hash_algorithm: str
    environment: str
    game_id: str
    ruleset_version: str
    match_id: str
    participants_hash: str
    participant_ordering: str
    replay_hash: str
    outcome_hash: str
    nonce: str
    verifier_version: str

    def to_canonical_dict(self) -> dict[str, object]:
        return {
            "domain": self.domain,
            "environment": self.environment,
            "game_id": self.game_id,
            "hash_algorithm": self.hash_algorithm,
            "match_id": self.match_id,
            "nonce": self.nonce,
            "outcome_hash": self.outcome_hash,
            "participant_ordering": self.participant_ordering,
            "participants_hash": self.participants_hash,
            "replay_hash": self.replay_hash,
            "ruleset_version": self.ruleset_version,
            "schema_version": self.schema_version,
            "verifier_version": self.verifier_version,
        }

    def digest(self) -> str:
        return "0x" + sha256_hex(self.to_canonical_dict())


def canonical_json(data: object) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(data: object) -> str:
    return hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest()


def participants_hash(participants: tuple[str, ...], *, ordering: str = "ordered") -> str:
    if ordering not in {"ordered", "unordered"}:
        raise ValueError(f"unsupported participant ordering: {ordering}")
    values = list(participants if ordering == "ordered" else tuple(sorted(participants)))
    return "0x" + sha256_hex({"ordering": ordering, "participants": values})


def outcome_hash(result: Mapping[str, object]) -> str:
    return "0x" + sha256_hex({"result": dict(result)})


def replay_hash(envelope: MatchEnvelope) -> str:
    return "0x" + envelope.digest()


def commitment_payload_for_envelope(
    envelope: MatchEnvelope,
    *,
    environment: str = "local",
    nonce: str = "",
    verifier_version: str = "local-verifier-1",
    participant_ordering: str = "ordered",
) -> ResultCommitmentPayload:
    return ResultCommitmentPayload(
        schema_version=COMMITMENT_SCHEMA_VERSION,
        domain=COMMITMENT_DOMAIN,
        hash_algorithm=COMMITMENT_HASH_ALGORITHM,
        environment=environment,
        game_id=envelope.game_id,
        ruleset_version=envelope.ruleset_version,
        match_id=envelope.match_id,
        participants_hash=participants_hash(envelope.players, ordering=participant_ordering),
        participant_ordering=participant_ordering,
        replay_hash=replay_hash(envelope),
        outcome_hash=outcome_hash(
            {
                "winner": envelope.result.winner,
                "scores": dict(envelope.result.scores),
                "terminal_reason": envelope.result.terminal_reason,
                "final_state_hash": envelope.final_state_hash,
            }
        ),
        nonce=nonce,
        verifier_version=verifier_version,
    )


def result_commitment_for_envelope(
    envelope: MatchEnvelope,
    *,
    environment: str = "local",
    nonce: str = "",
    verifier_version: str = "local-verifier-1",
) -> str:
    return commitment_payload_for_envelope(
        envelope,
        environment=environment,
        nonce=nonce,
        verifier_version=verifier_version,
    ).digest()
