"""Board construction and edge helpers."""

from .state import Edge, Point, SquareXOState


def edge_key(edge: Edge) -> str:
    start, end = ordered_points(edge.from_point, edge.to_point)
    return f"{start.row},{start.col}-{end.row},{end.col}"


def ordered_points(a: Point, b: Point) -> tuple[Point, Point]:
    return (a, b) if a <= b else (b, a)


def create_game(rows: int = 4, cols: int = 4) -> SquareXOState:
    if not isinstance(rows, int) or not isinstance(cols, int) or rows <= 0 or cols <= 0:
        raise ValueError("rows and cols must be positive integers")
    edges: list[Edge] = []
    for row in range(rows + 1):
        for col in range(cols):
            edges.append(Edge(Point(row, col), Point(row, col + 1)))
    for row in range(rows):
        for col in range(cols + 1):
            edges.append(Edge(Point(row, col), Point(row + 1, col)))
    return SquareXOState(rows=rows, cols=cols, edges=tuple(edges))


def is_edge_taken(state: SquareXOState, edge: Edge) -> bool:
    target = edge_key(edge)
    return any(edge_key(candidate) == target and candidate.taken_by is not None for candidate in state.edges)


def legal_edges(state: SquareXOState) -> tuple[Edge, ...]:
    if state.is_terminal:
        return tuple()
    return tuple(edge for edge in state.edges if edge.taken_by is None)
