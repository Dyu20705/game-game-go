"""Leaderboard and match history scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_leaderboard_scene(pygame, context) -> SceneResult:
    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    section_font = pygame.font.SysFont("segoeui", 24, bold=True)
    body_font = pygame.font.SysFont("segoeui", 18)
    button_font = pygame.font.SysFont("segoeui", 18, bold=True)

    while True:
        context.audio.update()
        back_rect = pygame.Rect(24, 24, 120, 44)
        width, height = screen.get_size()
        history = pygame.Rect(54, 130, max(320, width // 2 - 76), height - 190)
        friends = pygame.Rect(history.right + 24, 130, max(300, width - history.right - 78), height - 190)
        if width < 860:
            history = pygame.Rect(32, 118, width - 64, (height - 178) // 2)
            friends = pygame.Rect(32, history.bottom + 20, width - 64, height - history.bottom - 52)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.GAME_LIBRARY)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_rect.collidepoint(event.pos):
                return SceneResult(PlatformAction.GAME_LIBRARY)

        screen.fill(theme.BG)
        draw_button(pygame, screen, back_rect, "Back", button_font, color=theme.PANEL_ALT)
        draw_text(pygame, screen, title_font, "Leaderboard", (width // 2, 72))
        _panel(pygame, screen, history)
        _panel(pygame, screen, friends)
        screen.blit(section_font.render("Match History", True, theme.TEXT), (history.x + 24, history.y + 24))
        screen.blit(body_font.render("No matches yet.", True, theme.MUTED), (history.x + 24, history.y + 76))
        screen.blit(body_font.render("Play a game to start your history.", True, theme.SUBTLE), (history.x + 24, history.y + 106))
        screen.blit(section_font.render("Friends", True, theme.TEXT), (friends.x + 24, friends.y + 24))
        screen.blit(body_font.render("No friends ranking yet.", True, theme.MUTED), (friends.x + 24, friends.y + 76))
        screen.blit(body_font.render("Local profiles will appear here.", True, theme.SUBTLE), (friends.x + 24, friends.y + 106))
        pygame.display.flip()
        clock.tick(60)


def _panel(pygame, screen, rect):
    pygame.draw.rect(screen, theme.SIDEBAR, rect, border_radius=theme.RADIUS_LG)
    pygame.draw.rect(screen, theme.BORDER_SUBTLE, rect, 1, border_radius=theme.RADIUS_LG)
