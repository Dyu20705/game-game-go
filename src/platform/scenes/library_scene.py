"""Game library scene driven by GameRegistry."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text
from src.platform.ui.icons import draw_fallback_icon


def run_library_scene(pygame, context, registry) -> SceneResult:
    """Show registered games and return the selected game id."""

    screen = context.screen
    clock = context.clock
    loc = context.localization
    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    body_font = pygame.font.SysFont("segoeui", 18)
    button_font = pygame.font.SysFont("segoeui", 20, bold=True)

    while True:
        games = registry.list_all()
        cards = []
        width = min(760, screen.get_width() - 56)
        x = (screen.get_width() - width) // 2
        y = 145
        for index, game in enumerate(games):
            cards.append((pygame.Rect(x, y + index * 112, width, 92), game))
        back_rect = pygame.Rect(24, 24, 130, 44)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.HOME)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.HOME)
                for rect, game in cards:
                    if rect.collidepoint(event.pos) and game.descriptor.enabled:
                        return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)

        screen.fill(theme.BG)
        draw_button(pygame, screen, back_rect, loc.get("common.back"), button_font, color=theme.PANEL_ALT)
        draw_text(pygame, screen, title_font, loc.get("platform.library.title"), (screen.get_width() // 2, 70))

        if not games:
            draw_text(pygame, screen, body_font, loc.get("platform.library.empty"), (screen.get_width() // 2, 180), theme.MUTED)
        for rect, game in cards:
            descriptor = game.descriptor
            color = theme.PANEL if descriptor.enabled else (42, 42, 42)
            pygame.draw.rect(screen, color, rect, border_radius=8)
            pygame.draw.rect(screen, (221, 231, 238), rect, 1, border_radius=8)
            icon_rect = pygame.Rect(rect.x + 18, rect.y + 18, 56, 56)
            draw_fallback_icon(pygame, screen, icon_rect, descriptor.title, theme.BLUE if descriptor.enabled else theme.MUTED)
            title = body_font.render(descriptor.title, True, theme.TEXT)
            desc = body_font.render(descriptor.short_description, True, theme.MUTED)
            screen.blit(title, (rect.x + 92, rect.y + 20))
            screen.blit(desc, (rect.x + 92, rect.y + 50))
            if not descriptor.enabled:
                disabled = body_font.render(loc.get("common.disabled"), True, theme.AMBER)
                screen.blit(disabled, (rect.right - disabled.get_width() - 18, rect.y + 34))

        pygame.display.flip()
        clock.tick(60)

