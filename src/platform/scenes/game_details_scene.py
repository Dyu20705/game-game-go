"""About/help scene for the platform."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_about_scene(pygame, context) -> SceneResult:
    """Show a minimal platform about screen."""

    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    body_font = pygame.font.SysFont("segoeui", 22)
    button_font = pygame.font.SysFont("segoeui", 20, bold=True)

    while True:
        back_rect = pygame.Rect(24, 24, 130, 44)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.HOME)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_rect.collidepoint(event.pos):
                return SceneResult(PlatformAction.HOME)

        screen.fill(theme.BG)
        draw_button(pygame, screen, back_rect, context.localization.get("common.back"), button_font, color=theme.PANEL_ALT)
        draw_text(pygame, screen, title_font, "Game Game Go", (screen.get_width() // 2, 125))
        draw_text(pygame, screen, body_font, "A local desktop platform for small Pygame games.", (screen.get_width() // 2, 190), theme.MUTED)
        draw_text(pygame, screen, body_font, "Color Wars is now the first integrated mini-game.", (screen.get_width() // 2, 230), theme.MUTED)
        pygame.display.flip()
        clock.tick(60)

