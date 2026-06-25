import json
from pathlib import Path

from src.platform.blockchain.domain.commitment import ResultCommitmentPayload
from src.platform.blockchain.domain.result import CanonicalMatchResult, CanonicalMove, MatchEnvelope


def envelope_from_vector(data):
    result = data["result"]
    return MatchEnvelope(
        protocol_version=data["protocol_version"],
        game_id=data["game_id"],
        ruleset_version=data["ruleset_version"],
        match_id=data["match_id"],
        players=tuple(data["players"]),
        initial_state_hash=data["initial_state_hash"],
        moves=tuple(CanonicalMove(move["move_type"], move["payload"]) for move in data["moves"]),
        final_state_hash=data["final_state_hash"],
        result=CanonicalMatchResult(result["winner"], result["scores"], result["terminal_reason"]),
        metadata=data["metadata"],
    )


def test_result_commitment_vectors_are_stable():
    vectors = json.loads(Path("test_vectors/result_commitments.json").read_text(encoding="utf-8"))["vectors"]

    for vector in vectors:
        payload = ResultCommitmentPayload(**vector["payload"])
        assert payload.digest() == vector["commitment"]


def test_vector_envelope_digest_matches_payload_replay_hash():
    vector = json.loads(Path("test_vectors/result_commitments.json").read_text(encoding="utf-8"))["vectors"][0]
    envelope = envelope_from_vector(vector["envelope"])

    assert "0x" + envelope.digest() == vector["payload"]["replay_hash"]
