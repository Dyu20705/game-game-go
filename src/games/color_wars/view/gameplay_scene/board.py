"""Board rendering helpers."""

import pygame

from src.games.color_wars.engine.rules import EMPTY, PLAYER_BLUE

from ..constants import BLUE_COLOR, BORDER_WIDTH, CELL_BLUE_TINT, CELL_BORDER_COLOR, CELL_EMPTY_COLOR, CELL_RED_TINT, RED_COLOR


def drawNode(screen, rect, fill_color):
    """Draw a single board cell."""
    radius = max(6, int(min(rect.width, rect.height) * 0.16))
    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    pygame.draw.rect(screen, CELL_BORDER_COLOR, rect, BORDER_WIDTH, border_radius=radius)


def drawDot(screen, x, y, count, color, cell_size):
    """Draw 1..3 dots, or a four-corner fallback for larger counts."""
    cx = int(x + cell_size // 2)
    cy = int(y + cell_size // 2)
    radius = max(3, int(cell_size * 0.10))
    gap = max(6, int(cell_size * 0.17))

    if count == 1:
        positions = [(cx, cy)]
    elif count == 2:
        positions = [(cx - gap, cy), (cx + gap, cy)]
    elif count == 3:
        positions = [(cx - gap, cy), (cx + gap, cy), (cx, cy - gap)]
    else:
        positions = [
            (cx - gap, cy - gap),
            (cx + gap, cy - gap),
            (cx - gap, cy + gap),
            (cx + gap, cy + gap),
        ]

    for px, py in positions:
        pygame.draw.circle(screen, color, (px, py), radius)


def drawBoard(screen, board, dots, layout):
    """Render the board grid, ownership tint, and dots."""
    start_x = layout["board_x"]
    start_y = layout["board_y"]
    cell_size = layout["cell_size"]
    grid_size = len(board)

    for row in range(grid_size):
        for col in range(grid_size):
            x = int(start_x + col * cell_size)
            y = int(start_y + row * cell_size)
            pad = max(2, int(cell_size * 0.06))
            rect = pygame.Rect(
                x + pad,
                y + pad,
                max(6, int(cell_size) - pad * 2),
                max(6, int(cell_size) - pad * 2),
            )
            owner = board[row][col]
            if owner == PLAYER_BLUE:
                fill_color = CELL_BLUE_TINT
            elif owner == EMPTY:
                fill_color = CELL_EMPTY_COLOR
            else:
                fill_color = CELL_RED_TINT
            drawNode(screen, rect, fill_color)

            if board[row][col] == EMPTY or dots[row][col] <= 0:
                continue

            color = BLUE_COLOR if board[row][col] == PLAYER_BLUE else RED_COLOR
            drawDot(screen, x, y, dots[row][col], color, cell_size)

