"""Pygame rendering helpers for SquareXO."""

from math import hypot

from src.games.square_xo.domain.board import legal_edges
from src.games.square_xo.domain.state import Edge, Point, SquareXOState


COLORS = {
    "bg": (24, 30, 36),
    "panel": (39, 50, 59),
    "dot": (238, 244, 248),
    "empty": (105, 119, 130),
    "X": (94, 143, 231),
    "O": (185, 110, 216),
    "hover": (238, 173, 82),
    "text": (242, 246, 250),
    "muted": (181, 193, 203),
    "box_x": (45, 75, 128),
    "box_o": (91, 53, 120),
}


def board_rect(pygame, screen, state: SquareXOState):
    width, height = screen.get_size()
    board_size = min(width - 80, height - 190)
    cell = max(36, int(board_size / max(state.rows, state.cols)))
    total_w = state.cols * cell
    total_h = state.rows * cell
    return pygame.Rect((width - total_w) // 2, 120 + (height - 170 - total_h) // 2, total_w, total_h), cell


def point_to_screen(origin, cell: int, point: Point):
    return origin[0] + point.col * cell, origin[1] + point.row * cell


def draw_gameplay(pygame, screen, state: SquareXOState, hover: Edge | None, status: str):
    screen.fill(COLORS["bg"])
    rect, cell = board_rect(pygame, screen, state)
    font = pygame.font.SysFont("segoeui", 24, bold=True)
    small = pygame.font.SysFont("segoeui", 18)

    title = font.render("SquareXO", True, COLORS["text"])
    screen.blit(title, (28, 24))
    hud = small.render(
        f"Turn: {state.current_player.value}    X: {state.score_x}    O: {state.score_o}    {status}",
        True,
        COLORS["muted"],
    )
    screen.blit(hud, (28, 62))

    for box in state.boxes:
        color = COLORS["box_x"] if box.owner.value == "X" else COLORS["box_o"]
        box_rect = pygame.Rect(rect.x + box.col * cell + 4, rect.y + box.row * cell + 4, cell - 8, cell - 8)
        pygame.draw.rect(screen, color, box_rect, border_radius=6)

    hover_key = _edge_points_key(hover) if hover else None
    for edge in state.edges:
        start = point_to_screen(rect.topleft, cell, edge.from_point)
        end = point_to_screen(rect.topleft, cell, edge.to_point)
        color = COLORS["empty"]
        width = 4
        if edge.taken_by:
            color = COLORS[edge.taken_by.value]
            width = 6
        elif _edge_points_key(edge) == hover_key:
            color = COLORS["hover"]
            width = 6
        pygame.draw.line(screen, color, start, end, width)

    for row in range(state.rows + 1):
        for col in range(state.cols + 1):
            pygame.draw.circle(screen, COLORS["dot"], point_to_screen(rect.topleft, cell, Point(row, col)), 5)

    if state.is_terminal:
        winner = state.winner.value if state.winner else "Draw"
        overlay = font.render(f"Finished: {winner}    R: Restart    Esc: Library", True, COLORS["text"])
        screen.blit(overlay, overlay.get_rect(center=(screen.get_width() // 2, screen.get_height() - 42)))
    else:
        help_text = small.render("Click an open edge. Complete a square to keep your turn. Esc returns to library.", True, COLORS["muted"])
        screen.blit(help_text, help_text.get_rect(center=(screen.get_width() // 2, screen.get_height() - 34)))


def edge_from_mouse(pygame, screen, state: SquareXOState, pos, threshold: int = 12) -> Edge | None:
    rect, cell = board_rect(pygame, screen, state)
    closest = None
    closest_dist = threshold
    for edge in legal_edges(state):
        start = point_to_screen(rect.topleft, cell, edge.from_point)
        end = point_to_screen(rect.topleft, cell, edge.to_point)
        distance = point_to_segment_distance(pos[0], pos[1], start[0], start[1], end[0], end[1])
        if distance < closest_dist:
            closest = edge
            closest_dist = distance
    return closest


def point_to_segment_distance(px, py, x1, y1, x2, y2) -> float:
    dx = x2 - x1
    dy = y2 - y1
    denom = dx * dx + dy * dy
    if denom == 0:
        return hypot(px - x1, py - y1)
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / denom))
    return hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def _edge_points_key(edge: Edge | None):
    if edge is None:
        return None
    points = sorted((edge.from_point, edge.to_point))
    return points[0], points[1]

