"""Rewards coming soon scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_rewards_scene(pygame, context) -> SceneResult:
    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 42, bold=True)
    body_font = pygame.font.SysFont("segoeui", 20)
    button_font = pygame.font.SysFont("segoeui", 18, bold=True)

    while True:
        context.audio.update()
        back_rect = pygame.Rect(24, 24, 120, 44)
        width, height = screen.get_size()
        card = pygame.Rect(max(28, (width - 620) // 2), max(100, (height - 360) // 2), min(620, width - 56), 320)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.GAME_LIBRARY)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_rect.collidepoint(event.pos):
                return SceneResult(PlatformAction.GAME_LIBRARY)

        screen.fill(theme.BG)
        draw_button(pygame, screen, back_rect, "Back", button_font, color=theme.PANEL_ALT)
        pygame.draw.rect(screen, theme.SIDEBAR, card, border_radius=theme.RADIUS_XL)
        pygame.draw.rect(screen, theme.BORDER_SUBTLE, card, 1, border_radius=theme.RADIUS_XL)
        icon = pygame.Rect(card.centerx - 44, card.y + 44, 88, 88)
        pygame.draw.rect(screen, theme.PANEL, icon, border_radius=theme.RADIUS_LG)
        pygame.draw.circle(screen, theme.BRAND_PRIMARY, icon.center, 26)
        pygame.draw.circle(screen, theme.WARNING, icon.center, 11)
        draw_text(pygame, screen, title_font, "NFT Rewards", (card.centerx, card.y + 170))
        draw_text(
            pygame,
            screen,
            body_font,
            "Collectible rewards are being prepared.",
            (card.centerx, card.y + 220),
            theme.MUTED,
        )
        draw_text(pygame, screen, body_font, "Coming soon", (card.centerx, card.y + 258), theme.BRAND_PRIMARY)
        pygame.display.flip()
        clock.tick(60)
