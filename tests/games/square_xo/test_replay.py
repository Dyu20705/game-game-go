from src.games.square_xo.domain import ClaimEdge, Edge, Player, Point, create_game
from src.games.square_xo.domain.replay import envelope_for_replay, move_to_canonical, state_from_dict, state_hash, state_to_dict
from src.games.square_xo.application.result_submission import verify_square_xo_replay
from src.platform.blockchain.domain.commitment import result_commitment_for_envelope
from src.platform.blockchain.domain.result import CanonicalMatchResult, ReplayVerificationRequest


def edge(a, b, c, d):
    return Edge(Point(a, b), Point(c, d))


def test_state_serialization_round_trip_and_hash_is_deterministic():
    state = create_game(1, 1)
    restored = state_from_dict(state_to_dict(state))

    assert restored == state
    assert state_hash(restored) == state_hash(state)


def test_envelope_verifies_replay():
    initial = create_game(1, 1)
    moves = (
        ClaimEdge(edge(0, 0, 0, 1), Player.X),
        ClaimEdge(edge(0, 0, 1, 0), Player.O),
        ClaimEdge(edge(1, 0, 1, 1), Player.X),
        ClaimEdge(edge(0, 1, 1, 1), Player.O),
    )

    envelope = envelope_for_replay("test-match", initial, moves)
    verification = verify_square_xo_replay(ReplayVerificationRequest(envelope))

    assert verification.accepted is True
    assert verification.result_hash == result_commitment_for_envelope(envelope)


def test_tampered_replay_is_rejected():
    initial = create_game(1, 1)
    move = ClaimEdge(edge(0, 0, 0, 1), Player.X)
    envelope = envelope_for_replay("test-match", initial, (move,))
    tampered = type(envelope)(
        protocol_version=envelope.protocol_version,
        game_id=envelope.game_id,
        ruleset_version=envelope.ruleset_version,
        match_id=envelope.match_id,
        players=envelope.players,
        initial_state_hash=envelope.initial_state_hash,
        moves=(move_to_canonical(move),),
        final_state_hash="bad",
        result=envelope.result,
        metadata=envelope.metadata,
    )

    assert verify_square_xo_replay(ReplayVerificationRequest(tampered)).accepted is False


def test_mismatched_claimed_result_is_rejected():
    initial = create_game(1, 1)
    moves = (
        ClaimEdge(edge(0, 0, 0, 1), Player.X),
        ClaimEdge(edge(0, 0, 1, 0), Player.O),
        ClaimEdge(edge(1, 0, 1, 1), Player.X),
        ClaimEdge(edge(0, 1, 1, 1), Player.O),
    )
    envelope = envelope_for_replay("test-match", initial, moves)
    tampered = type(envelope)(
        protocol_version=envelope.protocol_version,
        game_id=envelope.game_id,
        ruleset_version=envelope.ruleset_version,
        match_id=envelope.match_id,
        players=envelope.players,
        initial_state_hash=envelope.initial_state_hash,
        moves=envelope.moves,
        final_state_hash=envelope.final_state_hash,
        result=CanonicalMatchResult("X", envelope.result.scores, envelope.result.terminal_reason),
        metadata=envelope.metadata,
    )

    result = verify_square_xo_replay(ReplayVerificationRequest(tampered))

    assert result.accepted is False
    assert result.reason == "result_mismatch"
