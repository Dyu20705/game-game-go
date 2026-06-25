from src.platform.blockchain.adapters.local import LocalIdentity, LocalMatchRegistry, LocalResultVerifier
from src.platform.blockchain.domain.match import CreateMatchRequest, MatchStatus, PlayerRef
from src.platform.blockchain.domain.result import (
    CanonicalMatchResult,
    MatchEnvelope,
    ReplayVerificationRequest,
    VerificationResult,
)
from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


def test_local_identity_signs_without_wallet():
    identity = LocalIdentity()

    result = identity.sign_challenge(b"abc")

    assert result.identity.kind.value == "guest_local"
    assert result.signature == b"local:abc"


def test_local_match_registry_create_and_submit_result():
    registry = LocalMatchRegistry()
    reference = registry.create_match(
        CreateMatchRequest("square_xo", "rules", (PlayerRef("x", "X"), PlayerRef("o", "O")))
    )
    envelope = MatchEnvelope(
        protocol_version="1",
        game_id="square_xo",
        ruleset_version="rules",
        match_id=reference.match_id,
        players=("X", "O"),
        initial_state_hash="a",
        moves=tuple(),
        final_state_hash="b",
        result=CanonicalMatchResult(winner=None, scores={"X": 0, "O": 0}, terminal_reason="draw"),
    )

    receipt = registry.submit_result(envelope)

    assert receipt.submitted is True
    assert registry.get_match(reference.match_id).status == MatchStatus.RESOLVED


def test_local_verifier_dispatches_by_game_id():
    verifier = LocalResultVerifier()
    verifier.register("square_xo", lambda request: VerificationResult(True, result_hash="ok"))
    envelope = MatchEnvelope(
        "1", "square_xo", "rules", "m", ("X", "O"), "a", tuple(), "b", CanonicalMatchResult(None, {}, "draw")
    )

    assert verifier.verify_replay(ReplayVerificationRequest(envelope)).accepted is True


def test_local_match_registry_rejects_duplicate_result():
    registry = LocalMatchRegistry()
    reference = registry.create_match(
        CreateMatchRequest("square_xo", "rules", (PlayerRef("x", "X"), PlayerRef("o", "O")))
    )
    envelope = MatchEnvelope(
        protocol_version="1",
        game_id="square_xo",
        ruleset_version="rules",
        match_id=reference.match_id,
        players=("X", "O"),
        initial_state_hash="a",
        moves=tuple(),
        final_state_hash="b",
        result=CanonicalMatchResult(winner=None, scores={"X": 0, "O": 0}, terminal_reason="draw"),
    )
    registry.submit_result(envelope)

    try:
        registry.submit_result(envelope)
    except BlockchainError as exc:
        assert exc.code == BlockchainErrorCode.INVALID_LIFECYCLE
    else:
        raise AssertionError("duplicate result was accepted")


def test_local_verifier_rejects_duplicate_registration():
    verifier = LocalResultVerifier()
    verifier.register("square_xo", lambda request: VerificationResult(True, result_hash="ok"))

    try:
        verifier.register("square_xo", lambda request: VerificationResult(True, result_hash="again"))
    except BlockchainError as exc:
        assert exc.code == BlockchainErrorCode.INVALID_LIFECYCLE
    else:
        raise AssertionError("duplicate verifier was accepted")
