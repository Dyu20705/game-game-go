"""Game Game Go home scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_home_scene(pygame, context) -> SceneResult:
    """Run the platform home scene until the user selects an action."""

    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 56, bold=True)
    button_font = pygame.font.SysFont("segoeui", 24, bold=True)
    body_font = pygame.font.SysFont("segoeui", 20)

    actions = [
        ("Browse games", PlatformAction.GAME_LIBRARY),
        ("Settings", PlatformAction.SETTINGS),
        ("Quit", PlatformAction.QUIT),
    ]

    while True:
        context.audio.update()
        width, height = screen.get_size()
        hero = pygame.Rect(0, 0, width, height)
        button_width = min(300, width - 48) if width < 760 else 260
        button_height = 56
        gap = 14
        start_x = (width - button_width) // 2 if width < 760 else 96
        start_y = min(height - 250, 380)
        play_rect = pygame.Rect(start_x, start_y, button_width, button_height)
        settings_rect = pygame.Rect(start_x, play_rect.bottom + gap, button_width, button_height)
        quit_rect = pygame.Rect(start_x, settings_rect.bottom + gap, button_width, button_height)
        rects = [play_rect, settings_rect, quit_rect]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, (_, action) in zip(rects, actions):
                    if rect.collidepoint(event.pos):
                        return SceneResult(action)

        _draw_home_background(pygame, screen, hero)
        title_x = 96 if width >= 760 else width // 2
        align_center = width < 760
        title_pos = (title_x, 190)
        if align_center:
            draw_text(pygame, screen, title_font, "Game Game Go", title_pos)
            draw_text(pygame, screen, body_font, "Ready for another round?", (title_x, 250), theme.MUTED)
        else:
            title_surface = title_font.render("Game Game Go", True, theme.TEXT)
            screen.blit(title_surface, (title_x, 160))
            body_surface = body_font.render("Ready for another round?", True, theme.MUTED)
            screen.blit(body_surface, (title_x + 4, 230))
        for rect, (label, action) in zip(rects, actions):
            color = theme.DANGER if action == PlatformAction.QUIT else theme.BRAND_PRIMARY
            if action == PlatformAction.SETTINGS:
                color = theme.PANEL_ALT
            draw_button(pygame, screen, rect, label, button_font, color=color)
        pygame.display.flip()
        clock.tick(60)


def _draw_home_background(pygame, screen, rect):
    screen.fill(theme.BG)
    width, height = rect.size
    center = (int(width * 0.68), int(height * 0.46))
    pygame.draw.circle(screen, (22, 44, 56), center, min(width, height) // 3)
    pygame.draw.circle(screen, (29, 65, 80), center, min(width, height) // 5, 2)
    for index, (dx, dy, color) in enumerate(
        (
            (-170, -90, theme.PLAYER_ONE),
            (-60, 80, theme.BRAND_PRIMARY),
            (120, -70, theme.WARNING),
            (200, 90, theme.SUCCESS),
            (20, -150, theme.INFO),
        )
    ):
        tile = pygame.Rect(center[0] + dx, center[1] + dy, 68, 68)
        pygame.draw.rect(screen, color, tile, border_radius=theme.RADIUS_LG)
        pygame.draw.rect(screen, (238, 245, 249), tile, 2, border_radius=theme.RADIUS_LG)
        pygame.draw.circle(screen, theme.BG, tile.center, 10 + index % 2 * 5)
    pygame.draw.line(screen, theme.BORDER, (center[0] - 150, center[1]), (center[0] + 230, center[1] + 30), 3)
