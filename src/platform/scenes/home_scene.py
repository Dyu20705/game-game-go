"""Game Game Go home scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import ButtonState, draw_button


def run_home_scene(pygame, context) -> SceneResult:
    """Run the platform home scene until the user selects an action."""

    screen = context.screen
    clock = context.clock
    button_font = context.assets.font(pygame, "body", 22, bold=True)
    body_font = context.assets.font(pygame, "body", 17)
    small_font = context.assets.font(pygame, "body", 13)
    scene_start = pygame.time.get_ticks()
    focused_index = 0
    pressed_index = None
    actions = [
        ("Play", PlatformAction.GAME_LIBRARY),
        ("Settings", PlatformAction.SETTINGS),
        ("Credits", PlatformAction.ABOUT),
        ("Quit", PlatformAction.QUIT),
    ]

    while True:
        context.audio.update()
        mouse_pos = pygame.mouse.get_pos()
        width, height = screen.get_size()
        layout = _compute_home_layout(pygame, width, height, len(actions))
        rects = layout["buttons"]
        hovered_index = next((index for index, rect in enumerate(rects) if rect.collidepoint(mouse_pos)), None)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return SceneResult(PlatformAction.QUIT)
                if event.key in (pygame.K_DOWN, pygame.K_TAB):
                    focused_index = (focused_index + 1) % len(actions)
                elif event.key == pygame.K_UP:
                    focused_index = (focused_index - 1) % len(actions)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    return SceneResult(actions[focused_index][1])
            if event.type == pygame.MOUSEMOTION and hovered_index is not None:
                focused_index = hovered_index
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pressed_index = None
                for index, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        pressed_index = index
                        focused_index = index
                        break
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for index, (rect, (_, action)) in enumerate(zip(rects, actions)):
                    if pressed_index == index and rect.collidepoint(event.pos):
                        return SceneResult(action)
                pressed_index = None

        _draw_home_background(pygame, screen, context)
        _draw_brand_panel(pygame, screen, context, layout, scene_start, body_font, small_font)
        for index, (rect, (label, action)) in enumerate(zip(rects, actions)):
            color = theme.DANGER if action == PlatformAction.QUIT else theme.BRAND_PRIMARY
            if action == PlatformAction.SETTINGS:
                color = theme.PANEL_ALT
            if action == PlatformAction.ABOUT:
                color = (112, 116, 232)
            draw_button(
                pygame,
                screen,
                rect,
                label,
                button_font,
                color=color,
                state=ButtonState(
                    hovered=index == hovered_index,
                    pressed=index == pressed_index,
                    focused=index == focused_index,
                ),
            )
        pygame.display.flip()
        clock.tick(60)


def _compute_home_layout(pygame, width: int, height: int, button_count: int) -> dict[str, object]:
    safe_x = max(24, int(width * 0.055))
    safe_y = max(24, int(height * 0.07))
    panel_width = min(560, width - safe_x * 2)
    panel_height = min(height - safe_y * 2, max(520, int(height * 0.76)))
    panel_x = safe_x if width >= 900 else (width - panel_width) // 2
    panel = pygame.Rect(panel_x, (height - panel_height) // 2, panel_width, panel_height)
    button_width = min(340, panel.width - 80)
    button_height = 56
    gap = 14
    buttons_total = button_count * button_height + (button_count - 1) * gap
    start_y = min(panel.bottom - buttons_total - 46, panel.y + int(panel.height * 0.52))
    start_y = max(panel.y + 270, start_y)
    button_x = panel.x + (panel.width - button_width) // 2
    buttons = [
        pygame.Rect(button_x, start_y + index * (button_height + gap), button_width, button_height)
        for index in range(button_count)
    ]
    logo_box = pygame.Rect(panel.x + 48, panel.y + 52, panel.width - 96, max(160, min(250, panel.height // 3)))
    return {"panel": panel, "buttons": buttons, "logo_box": logo_box}


def _draw_home_background(pygame, screen, context) -> None:
    background = context.assets.cover_image(
        pygame,
        context.assets.background("menu_background_1920x1080.png"),
        screen.get_size(),
        focal=(0.5, 0.52),
    )
    screen.blit(background, (0, 0))
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((16, 26, 42, 26))
    screen.blit(veil, (0, 0))


def _draw_brand_panel(pygame, screen, context, layout, scene_start: int, body_font, small_font) -> None:
    panel = layout["panel"]
    logo_box = layout["logo_box"]
    elapsed = pygame.time.get_ticks() - scene_start
    intro = min(1.0, elapsed / 240)
    offset = int((1.0 - _ease_out(intro)) * 10)

    panel_surface = pygame.Surface(panel.size, pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (255, 255, 255, 158), panel_surface.get_rect(), border_radius=theme.RADIUS_XL)
    pygame.draw.rect(panel_surface, (255, 255, 255, 116), panel_surface.get_rect(), 2, border_radius=theme.RADIUS_XL)
    screen.blit(panel_surface, panel.move(0, offset))

    logo = context.assets.image(pygame, context.assets.branding("game_logo_full_runtime.png"), fallback_size=(420, 250))
    logo_size = _fit_size((logo.get_width(), logo.get_height()), logo_box.size)
    logo_surface = pygame.transform.smoothscale(logo, logo_size)
    logo_surface.set_alpha(int(255 * _ease_out(intro)))
    logo_rect = logo_surface.get_rect(center=logo_box.move(0, offset).center)
    screen.blit(logo_surface, logo_rect)

    tagline = body_font.render("", True, (71, 81, 102))
    screen.blit(tagline, tagline.get_rect(center=(panel.centerx, logo_box.bottom + 34 + offset)))
    studio = small_font.render("Chillody Studio", True, (150, 105, 132))
    screen.blit(studio, studio.get_rect(center=(panel.centerx, panel.bottom - 26 + offset)))


def _fit_size(source_size: tuple[int, int], target_size: tuple[int, int]) -> tuple[int, int]:
    source_w, source_h = source_size
    target_w, target_h = target_size
    scale = min(target_w / source_w, target_h / source_h)
    return max(1, int(source_w * scale)), max(1, int(source_h * scale))


def _ease_out(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return 1.0 - (1.0 - value) ** 3
