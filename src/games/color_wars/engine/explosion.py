"""Engine nổ dây chuyền theo BFS."""

from collections import deque

from .rules import EMPTY, get_capacity, in_bounds

DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def resolve_explosions(board, dots, start_row, start_col, step_callback=None):
    """Giải nổ dây chuyền bắt đầu từ ô vừa được cập nhật."""
    size = len(board)
    queue = deque([(start_row, start_col)])

    while queue:
        # Lấy từng ô cần kiểm tra nổ theo thứ tự BFS.
        row, col = queue.popleft()
        owner = board[row][col]

        if owner == EMPTY:
            continue

        if dots[row][col] < get_capacity(row, col, size):
            continue

        dots[row][col] = 0
        board[row][col] = EMPTY
        spread_targets = []

        # Phát tán 1 dot sang 4 hướng và đồng hóa màu theo chủ ô gây nổ.
        for dr, dc in DIRECTIONS:
            nr, nc = row + dr, col + dc
            if not in_bounds(nr, nc, size):
                continue

            board[nr][nc] = owner
            dots[nr][nc] += 1
            spread_targets.append((nr, nc))

            # Nếu ô nhận dot đạt ngưỡng thì đưa vào hàng đợi để nổ tiếp.
            if dots[nr][nc] >= get_capacity(nr, nc, size):
                queue.append((nr, nc))

        if step_callback is not None:
            step_callback(
                {
                    "center": (row, col),
                    "owner": owner,
                    "targets": spread_targets,
                }
            )
