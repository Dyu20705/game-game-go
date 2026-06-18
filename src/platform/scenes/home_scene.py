"""Game Game Go home scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text
from src.platform.ui.layout import centered_button_rects


def run_home_scene(pygame, context) -> SceneResult:
    """Run the platform home scene until the user selects an action."""

    screen = context.screen
    clock = context.clock
    loc = context.localization
    title_font = pygame.font.SysFont("segoeui", 56, bold=True)
    button_font = pygame.font.SysFont("segoeui", 24, bold=True)
    body_font = pygame.font.SysFont("segoeui", 20)

    actions = [
        (loc.get("platform.home.play"), PlatformAction.GAME_LIBRARY),
        (loc.get("platform.home.settings"), PlatformAction.SETTINGS),
        (loc.get("platform.home.help"), PlatformAction.ABOUT),
        (loc.get("platform.home.quit"), PlatformAction.QUIT),
    ]

    while True:
        rects = centered_button_rects(pygame, screen, len(actions))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, (_, action) in zip(rects, actions):
                    if rect.collidepoint(event.pos):
                        return SceneResult(action)

        screen.fill(theme.BG)
        draw_text(pygame, screen, title_font, loc.get("platform.home.title"), (screen.get_width() // 2, 120))
        draw_text(pygame, screen, body_font, "Desktop mini-game platform", (screen.get_width() // 2, 170), theme.MUTED)
        for rect, (label, action) in zip(rects, actions):
            color = theme.DANGER if action == PlatformAction.QUIT else theme.PANEL_ALT
            draw_button(pygame, screen, rect, label, button_font, color=color)
        pygame.display.flip()
        clock.tick(60)

