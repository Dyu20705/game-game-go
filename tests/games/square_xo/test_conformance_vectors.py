import json

from src.games.square_xo.domain import ClaimEdge, Edge, Player, Point, apply_move, create_game


def test_square_xo_vectors_match_source_behavior():
    with open("tests/conformance/square_xo_vectors/basic_vectors.json", "r", encoding="utf-8") as handle:
        vectors = json.load(handle)

    for vector in vectors:
        state = create_game(vector["rows"], vector["cols"])
        for item in vector["moves"]:
            move = ClaimEdge(
                Edge(
                    Point(item["from"]["row"], item["from"]["col"]),
                    Point(item["to"]["row"], item["to"]["col"]),
                ),
                Player(item["player"]),
            )
            state = apply_move(state, move)

        assert state.score == vector["expected"]["score"], vector["name"]
        assert state.current_player.value == vector["expected"]["currentPlayer"], vector["name"]
        assert [
            {"row": box.row, "col": box.col, "owner": box.owner.value}
            for box in state.boxes
        ] == vector["expected"]["boxes"], vector["name"]

