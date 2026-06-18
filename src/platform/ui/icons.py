"""Placeholder icon helpers for platform scenes."""


def draw_fallback_icon(pygame, screen, rect, label, color):
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (240, 246, 250), rect, 2, border_radius=8)
    font = pygame.font.SysFont("segoeui", max(16, rect.height // 3), bold=True)
    text = font.render(label[:2].upper(), True, (255, 255, 255))
    screen.blit(text, text.get_rect(center=rect.center))

