import pytest

from src.games.square_xo.domain import ClaimEdge, Edge, Player, Point, apply_move, create_game, is_edge_taken


def edge(a, b, c, d):
    return Edge(Point(a, b), Point(c, d))


def test_create_game_matches_source_edge_count():
    state = create_game(2, 3)

    assert state.rows == 2
    assert state.cols == 3
    assert state.current_player == Player.X
    assert len(state.edges) == (2 + 1) * 3 + 2 * (3 + 1)


def test_apply_move_is_immutable_and_direction_independent():
    initial = create_game(1, 1)
    top = edge(0, 0, 0, 1)
    moved = apply_move(initial, ClaimEdge(edge(0, 1, 0, 0), Player.X))

    assert moved is not initial
    assert not is_edge_taken(initial, top)
    assert is_edge_taken(moved, top)


def test_invalid_duplicate_and_wrong_player_moves_fail():
    state = create_game(1, 1)

    with pytest.raises(ValueError, match="Invalid edge"):
        apply_move(state, ClaimEdge(edge(0, 0, 1, 1), Player.X))
    with pytest.raises(ValueError, match="Only the current player"):
        apply_move(state, ClaimEdge(edge(0, 0, 0, 1), Player.O))

    moved = apply_move(state, ClaimEdge(edge(0, 0, 0, 1), Player.X))
    with pytest.raises(ValueError, match="Edge already taken"):
        apply_move(moved, ClaimEdge(edge(0, 0, 0, 1), Player.O))


def test_completing_square_scores_and_keeps_turn_like_source():
    state = create_game(1, 1)
    state = apply_move(state, ClaimEdge(edge(0, 0, 0, 1), Player.X))
    state = apply_move(state, ClaimEdge(edge(0, 0, 1, 0), Player.O))
    state = apply_move(state, ClaimEdge(edge(1, 0, 1, 1), Player.X))
    state = apply_move(state, ClaimEdge(edge(0, 1, 1, 1), Player.O))

    assert state.score == {"X": 0, "O": 1}
    assert state.current_player == Player.O
    assert state.is_terminal
    assert state.winner == Player.O
