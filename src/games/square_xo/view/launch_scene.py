"""SquareXO launch configuration scene."""

from src.platform.games import GameLaunchOptions


def run_square_xo_launch_scene(context) -> GameLaunchOptions | None:
    import pygame

    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    body_font = pygame.font.SysFont("segoeui", 20)
    button_font = pygame.font.SysFont("segoeui", 20, bold=True)
    board_size = 4
    blockchain_mode = "LOCAL_MOCK"

    def button(rect, label, active=False):
        color = (76, 150, 116) if active else (48, 60, 70)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (230, 238, 244), rect, 1, border_radius=8)
        text = button_font.render(label, True, (242, 246, 250))
        screen.blit(text, text.get_rect(center=rect.center))

    while True:
        width, height = screen.get_size()
        back_rect = pygame.Rect(24, 24, 130, 44)
        size_rects = [
            pygame.Rect(width // 2 - 260 + index * 180, 220, 150, 54)
            for index in range(3)
        ]
        offline_rect = pygame.Rect(width // 2 - 230, 315, 210, 54)
        mock_rect = pygame.Rect(width // 2 + 20, 315, 210, 54)
        start_rect = pygame.Rect(width // 2 - 150, height - 130, 300, 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return None
                for rect, size in zip(size_rects, (3, 4, 5)):
                    if rect.collidepoint(event.pos):
                        board_size = size
                if offline_rect.collidepoint(event.pos):
                    blockchain_mode = "OFFLINE"
                if mock_rect.collidepoint(event.pos):
                    blockchain_mode = "LOCAL_MOCK"
                if start_rect.collidepoint(event.pos):
                    return GameLaunchOptions(
                        mode="local_1v1",
                        custom={"rows": board_size, "cols": board_size, "blockchain_mode": blockchain_mode, "stake_mode": "NO_STAKE"},
                    )

        screen.fill((22, 28, 34))
        title = title_font.render("SquareXO", True, (242, 246, 250))
        screen.blit(title, title.get_rect(center=(width // 2, 92)))
        subtitle = body_font.render("Local 1v1. No real-money wagering. Oasis mode is local/mock by default.", True, (181, 193, 203))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, 142)))
        button(back_rect, context.localization.get("common.back"))
        for rect, size in zip(size_rects, (3, 4, 5)):
            button(rect, f"{size}x{size}", board_size == size)
        button(offline_rect, "Offline", blockchain_mode == "OFFLINE")
        button(mock_rect, "Local Mock", blockchain_mode == "LOCAL_MOCK")
        button(start_rect, context.localization.get("common.start"), True)
        pygame.display.flip()
        clock.tick(60)

