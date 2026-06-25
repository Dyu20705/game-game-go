"""Responsive layout computation for both gameplay and menu scenes."""


def compute_layout(screen, grid_size):
    """Compute the current screen layout for the board and HUD.

    Args:
        screen: Pygame display surface
        grid_size: Number of cells per side (usually 5)

    Returns:
        dict with keys: width, height, side_margin, top_hud_height,
                       board_x, board_y, board_size, cell_size
    """
    width, height = screen.get_size()
    side_margin = max(10, int(min(width, height) * 0.02))
    top_hud_height = max(48, int(height * 0.11))
    available_w = max(100, width - side_margin * 2)
    available_h = max(100, height - top_hud_height - side_margin)

    board_size = min(available_w, available_h)
    board_x = (width - board_size) // 2
    board_y = top_hud_height + (available_h - board_size) // 2
    cell_size = board_size / max(1, grid_size)

    return {
        "width": width,
        "height": height,
        "side_margin": side_margin,
        "top_hud_height": top_hud_height,
        "board_x": board_x,
        "board_y": board_y,
        "board_size": board_size,
        "cell_size": cell_size,
    }


def get_cell_from_mouse(mouse_pos, grid_size, screen):
    """Convert a mouse position to a board cell, or return (None, None).

    Args:
        mouse_pos: (x, y) tuple from pygame event
        grid_size: Number of cells per side
        screen: Pygame display surface

    Returns:
        (row, col) tuple or (None, None) if outside board
    """
    layout = compute_layout(screen, grid_size)
    start_x = layout["board_x"]
    start_y = layout["board_y"]
    board_size = layout["board_size"]
    cell_size = layout["cell_size"]
    x, y = mouse_pos

    local_x = x - start_x
    local_y = y - start_y

    if local_x < 0 or local_y < 0:
        return None, None
    if local_x >= board_size or local_y >= board_size:
        return None, None

    col = int(local_x // cell_size)
    row = int(local_y // cell_size)

    if 0 <= row < grid_size and 0 <= col < grid_size:
        return row, col
    return None, None


def _cell_center(layout, row, col):
    """Return the pixel center of a board cell.

    Args:
        layout: dict from compute_layout()
        row, col: cell coordinates

    Returns:
        (cx, cy) pixel coordinate
    """
    cell_size = layout["cell_size"]
    cx = int(layout["board_x"] + col * cell_size + cell_size / 2)
    cy = int(layout["board_y"] + row * cell_size + cell_size / 2)
    return cx, cy
