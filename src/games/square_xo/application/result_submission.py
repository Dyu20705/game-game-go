"""SquareXO replay verification and local result submission helpers."""

from src.platform.blockchain.domain.result import ReplayVerificationRequest, VerificationResult

from src.games.square_xo.domain.replay import RULESET_VERSION, apply_replay, state_hash


def verify_square_xo_replay(request: ReplayVerificationRequest) -> VerificationResult:
    envelope = request.envelope
    if envelope.ruleset_version != RULESET_VERSION:
        return VerificationResult(False, reason="ruleset_mismatch")
    rows = int(envelope.metadata.get("rows", 4))
    cols = int(envelope.metadata.get("cols", 4))
    try:
        final = apply_replay(rows, cols, envelope.moves)
    except ValueError as exc:
        return VerificationResult(False, reason=str(exc))
    final_hash = state_hash(final)
    if final_hash != envelope.final_state_hash:
        return VerificationResult(False, reason="final_state_hash_mismatch")
    return VerificationResult(True, result_hash=envelope.digest())

