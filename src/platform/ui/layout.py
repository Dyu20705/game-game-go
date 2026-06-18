"""Layout helpers for platform scenes."""


def centered_button_rects(pygame, screen, count: int, width: int = 280, height: int = 54, gap: int = 16):
    sw, sh = screen.get_size()
    total = count * height + max(0, count - 1) * gap
    start_y = (sh - total) // 2 + 48
    return [
        pygame.Rect((sw - width) // 2, start_y + index * (height + gap), width, height)
        for index in range(count)
    ]

