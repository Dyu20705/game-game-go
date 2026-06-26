"""About/help scene for the platform."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import ButtonState, draw_button, draw_text


def run_about_scene(pygame, context) -> SceneResult:
    """Show a minimal platform about screen."""

    screen = context.screen
    clock = context.clock
    title_font = context.assets.font(pygame, "display", 34, bold=True)
    body_font = context.assets.font(pygame, "body", 19)
    small_font = context.assets.font(pygame, "body", 15)
    button_font = context.assets.font(pygame, "body", 20, bold=True)

    while True:
        back_rect = pygame.Rect(24, 24, 130, 44)
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return SceneResult(PlatformAction.HOME)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_rect.collidepoint(event.pos):
                return SceneResult(PlatformAction.HOME)

        background = context.assets.cover_image(
            pygame, context.assets.background("menu_background_1920x1080.png"), screen.get_size()
        )
        screen.blit(background, (0, 0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((18, 27, 42, 44))
        screen.blit(overlay, (0, 0))
        panel = pygame.Rect(
            max(24, (screen.get_width() - 760) // 2),
            max(72, (screen.get_height() - 560) // 2),
            min(760, screen.get_width() - 48),
            min(560, screen.get_height() - 116),
        )
        panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (255, 255, 255, 172), panel_surface.get_rect(), border_radius=theme.RADIUS_XL)
        pygame.draw.rect(
            panel_surface, (255, 255, 255, 122), panel_surface.get_rect(), 2, border_radius=theme.RADIUS_XL
        )
        screen.blit(panel_surface, panel)
        draw_button(
            pygame,
            screen,
            back_rect,
            context.localization.get("common.back"),
            button_font,
            color=theme.PANEL_ALT,
            state=ButtonState(hovered=back_rect.collidepoint(mouse_pos), focused=True),
        )

        logo = context.assets.image(
            pygame, context.assets.branding("game_logo_full_runtime.png"), fallback_size=(360, 220)
        )
        logo_size = _fit_size((logo.get_width(), logo.get_height()), (min(420, panel.width - 96), 180))
        logo = pygame.transform.smoothscale(logo, logo_size)
        screen.blit(logo, logo.get_rect(center=(panel.centerx, panel.y + 132)))

        studio = context.assets.image(
            pygame, context.assets.branding("studio_logo_runtime.png"), fallback_size=(120, 120)
        )
        studio = pygame.transform.smoothscale(studio, (116, 116))
        screen.blit(studio, studio.get_rect(center=(panel.centerx, panel.y + 278)))

        draw_text(pygame, screen, title_font, "Chillody Studio", (panel.centerx, panel.y + 365), (91, 69, 86))
        lines = (
            "Game Game Go is a local-first desktop hub for small Pygame games.",
            "Built for expandable mini-games, polished menus and offline play.",
            "Blockchain and ROFL integrations are pre-production test scaffolds.",
        )
        for index, line in enumerate(lines):
            draw_text(pygame, screen, body_font, line, (panel.centerx, panel.y + 412 + index * 30), (71, 81, 102))
        draw_text(
            pygame,
            screen,
            small_font,
            "Product: Game Game Go  |  Studio: Chillody Studio",
            (panel.centerx, panel.bottom - 34),
            (132, 96, 118),
        )
        pygame.display.flip()
        clock.tick(60)


def _fit_size(source_size: tuple[int, int], target_size: tuple[int, int]) -> tuple[int, int]:
    source_w, source_h = source_size
    target_w, target_h = target_size
    scale = min(target_w / source_w, target_h / source_h)
    return max(1, int(source_w * scale)), max(1, int(source_h * scale))
