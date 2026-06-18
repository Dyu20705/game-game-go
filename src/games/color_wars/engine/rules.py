"""Bộ luật dùng chung giữa controller và AI."""

EMPTY = 0
PLAYER_BLUE = 1
PLAYER_RED = 2

EXPLOSION_THRESHOLD = 4
NEWHOLD = 3
OLDHOLD = 1

def in_bounds(row, col, size):
    """Kiểm tra tọa độ (row, col) có nằm trong bàn cờ hay không."""
    return 0 <= row < size and 0 <= col < size


def get_capacity(row, col, size):
    """Ngưỡng nổ của một ô (hiện tại cố định = 4)."""
    return EXPLOSION_THRESHOLD


def get_valid_moves(board, player):
    """Lượt đầu: đánh ô trống. Lượt sau: chỉ đánh ô đang sở hữu."""
    size = len(board)
    own_cells = []
    empty_cells = []

    for row in range(size):
        for col in range(size):
            if board[row][col] == player:
                own_cells.append((row, col))
            elif board[row][col] == EMPTY:
                empty_cells.append((row, col))

    # Khi đã có ô của mình, chỉ được chơi trên các ô đó.
    if own_cells:
        return own_cells

    # Chưa có ô nào -> chỉ được chọn ô trống để nhập cuộc.
    return empty_cells


def get_move_dot_increment(board, row, col):
    """Ô trống khi chiếm mới +3 dot; ô đã sở hữu thì +1 dot."""
    if board[row][col] == EMPTY:
        return NEWHOLD

    return OLDHOLD


