"""Controller-friendly hero and horizontal game shelf for Game Game Go."""

from __future__ import annotations

from dataclasses import dataclass

from src.platform.games import GameCapability
from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import ButtonState, draw_button, draw_focus_ring, draw_pill

TOP_BAR_HEIGHT = 76
FOOTER_HEIGHT = 50
SHELF_MIN_HEIGHT = 188


@dataclass(frozen=True)
class ArcadeShelfLayout:
    top_bar: object
    hero: object
    shelf: object
    footer: object


def compute_arcade_shelf_layout(pygame, screen_size) -> ArcadeShelfLayout:
    """Return responsive hero, shelf and footer rectangles."""

    width, height = screen_size
    margin = max(18, min(36, width // 48))
    top_bar = pygame.Rect(0, 0, width, TOP_BAR_HEIGHT)
    footer = pygame.Rect(0, height - FOOTER_HEIGHT, width, FOOTER_HEIGHT)
    content_top = top_bar.bottom + margin
    content_bottom = footer.top - margin
    content_height = max(320, content_bottom - content_top)
    shelf_height = max(SHELF_MIN_HEIGHT, min(238, int(content_height * 0.34)))
    hero_height = max(210, content_height - shelf_height - margin)
    hero = pygame.Rect(margin, content_top, width - margin * 2, hero_height)
    shelf = pygame.Rect(margin, hero.bottom + margin, hero.width, shelf_height)
    return ArcadeShelfLayout(top_bar, hero, shelf, footer)


def compute_shelf_cards(pygame, shelf_rect, count: int, selected_index: int = 0):
    """Lay out horizontal 16:9 cards while keeping the selected card visible."""

    if count <= 0:
        return []
    gap = max(12, min(22, shelf_rect.width // 60))
    card_height = max(116, shelf_rect.height - 48)
    card_width = max(172, min(272, int(card_height * 16 / 9)))
    total_width = count * card_width + (count - 1) * gap
    if total_width <= shelf_rect.width:
        start_x = shelf_rect.x + (shelf_rect.width - total_width) // 2
    else:
        selected_center = selected_index * (card_width + gap) + card_width // 2
        start_x = shelf_rect.centerx - selected_center
        start_x = max(shelf_rect.right - total_width, min(shelf_rect.x, start_x))
    y = shelf_rect.y + 40
    return [
        pygame.Rect(start_x + index * (card_width + gap), y, card_width, card_height)
        for index in range(count)
    ]


def _fit_surface(font, text: str, max_width: int, color):
    label = text
    surface = font.render(label, True, color)
    while surface.get_width() > max_width and len(label) > 4:
        label = label[:-4].rstrip() + "..."
        surface = font.render(label, True, color)
    return surface


def _wrap_lines(font, text: str, max_width: int, max_lines: int = 2) -> list[str]:
    lines: list[str] = []
    current = ""
    words = text.split()
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and " ".join(lines) != text:
        value = lines[-1] + "..."
        while font.size(value)[0] > max_width and len(value) > 4:
            value = value[:-4].rstrip() + "..."
        lines[-1] = value
    return lines


def _panel(pygame, screen, rect, fill, border, radius=theme.RADIUS_LG):
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 1, border_radius=radius)


def _player_label(descriptor) -> str:
    if descriptor.min_players == descriptor.max_players:
        suffix = "s" if descriptor.max_players != 1 else ""
        return f"{descriptor.max_players} Player{suffix}"
    return f"{descriptor.min_players}-{descriptor.max_players} Players"


def _primary_tag(descriptor) -> str:
    ignored = {"single-player", "1v1", "ai", "local", "turn-based"}
    tag = next((value for value in descriptor.tags if value not in ignored), "mini-game")
    return tag.replace("-", " ").title()


def _has_verified_mode(descriptor) -> bool:
    verified = {
        GameCapability.ONLINE_MULTIPLAYER,
        GameCapability.CONFIDENTIAL_MATCH,
        GameCapability.VERIFIED_RESULT,
    }
    return any(capability in verified for capability in descriptor.capabilities)


def _draw_background(pygame, screen, context, descriptor):
    image = context.assets.cover_image(pygame, descriptor.thumbnail, screen.get_size(), focal=(0.5, 0.45))
    screen.blit(image, (0, 0))
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((7, 12, 19, 210))
    screen.blit(veil, (0, 0))


def _draw_top_bar(pygame, screen, context, rect, fonts, settings_rect, credits_rect):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((9, 15, 23, 230))
    screen.blit(surface, rect)
    pygame.draw.line(screen, theme.BORDER, (0, rect.bottom - 1), (rect.width, rect.bottom - 1))
    logo_rect = pygame.Rect(24, 14, 48, 48)
    logo = context.assets.scaled_image(pygame, context.assets.branding("app_icon_64.png"), logo_rect.size)
    screen.blit(logo, logo_rect)
    title = fonts["top"].render("Game Game Go", True, theme.TEXT)
    screen.blit(title, (logo_rect.right + 12, 22))
    if rect.width >= 860:
        badge = pygame.Rect(logo_rect.right + title.get_width() + 28, 23, 98, 30)
        draw_pill(
            pygame,
            screen,
            badge,
            "LOCAL ARCADE",
            fonts["tiny"],
            (28, 51, 63),
            theme.FOCUS,
            (55, 93, 107),
        )
    mouse = pygame.mouse.get_pos()
    draw_button(
        pygame,
        screen,
        credits_rect,
        "Credits",
        fonts["small_bold"],
        color=theme.PANEL_ALT,
        state=ButtonState(hovered=credits_rect.collidepoint(mouse)),
    )
    draw_button(
        pygame,
        screen,
        settings_rect,
        "Settings",
        fonts["small_bold"],
        color=theme.PANEL_ALT,
        state=ButtonState(hovered=settings_rect.collidepoint(mouse)),
    )


def _draw_hero(pygame, screen, context, rect, fonts, game, play_rect, info_rect):
    descriptor = game.descriptor
    pygame.draw.rect(screen, (2, 5, 9), rect.move(0, 8), border_radius=theme.RADIUS_XL)
    art = context.assets.cover_image(pygame, descriptor.thumbnail, rect.size, focal=(0.62, 0.48))
    previous_clip = screen.get_clip()
    screen.set_clip(rect)
    screen.blit(art, rect)
    gradient = pygame.Surface(rect.size, pygame.SRCALPHA)
    for index in range(16):
        ratio = index / 15
        alpha = int(240 * (1 - ratio) ** 1.55)
        x = int(rect.width * ratio * 0.84)
        pygame.draw.rect(gradient, (6, 11, 18, alpha), (x, 0, rect.width // 15 + 6, rect.height))
    pygame.draw.rect(gradient, (4, 8, 13, 105), (0, rect.height - 110, rect.width, 110))
    screen.blit(gradient, rect)
    screen.set_clip(previous_clip)
    pygame.draw.rect(screen, (83, 104, 121), rect, 1, border_radius=theme.RADIUS_XL)

    left = rect.x + max(28, min(58, rect.width // 24))
    max_width = min(610, int(rect.width * 0.58))
    top = rect.y + max(24, int(rect.height * 0.11))
    screen.blit(fonts["tiny"].render("FEATURED IN YOUR ARCADE", True, theme.FOCUS), (left, top))
    title = _fit_surface(fonts["hero"], descriptor.title, max_width, theme.TEXT)
    screen.blit(title, (left, top + 28))
    y = top + 28 + title.get_height() + 12
    max_lines = 1 if rect.height < 300 else 2
    for line in _wrap_lines(fonts["body"], descriptor.short_description, max_width, max_lines):
        screen.blit(fonts["body"].render(line, True, (211, 220, 227)), (left, y))
        y += 27
    y += 8
    pills = (
        (_player_label(descriptor), theme.BLUE),
        (_primary_tag(descriptor), (75, 91, 108)),
        ("Offline", (53, 116, 76)),
    )
    x = left
    for label, fill in pills:
        width = max(74, fonts["small_bold"].size(label)[0] + 28)
        draw_pill(pygame, screen, pygame.Rect(x, y, width, 32), label, fonts["small_bold"], fill)
        x += width + 10
    if _has_verified_mode(descriptor) and rect.height >= 340:
        note = fonts["small"].render("Verified mode is available from this game's setup flow.", True, theme.MUTED)
        screen.blit(note, (left, y + 42))

    mouse = pygame.mouse.get_pos()
    draw_button(
        pygame,
        screen,
        play_rect,
        "PLAY NOW",
        fonts["button"],
        color=theme.BRAND_PRIMARY,
        state=ButtonState(hovered=play_rect.collidepoint(mouse), focused=True),
    )
    draw_button(
        pygame,
        screen,
        info_rect,
        "GAME INFO",
        fonts["button"],
        color=theme.PANEL_ALT,
        state=ButtonState(hovered=info_rect.collidepoint(mouse)),
    )


def _draw_card(pygame, screen, context, rect, fonts, game, selected, hover):
    lift = int(7 * max(hover, 1.0 if selected else 0.0))
    card = rect.move(0, -lift)
    pygame.draw.rect(screen, (2, 5, 9), card.move(0, 7), border_radius=theme.RADIUS_LG)
    art = context.assets.cover_image(pygame, game.descriptor.thumbnail, card.size)
    clip = screen.get_clip()
    screen.set_clip(card)
    screen.blit(art, card)
    shade = pygame.Surface(card.size, pygame.SRCALPHA)
    shade.fill((6, 10, 16, 30 if selected else 86))
    pygame.draw.rect(shade, (4, 8, 13, 205), (0, card.height - 54, card.width, 54))
    screen.blit(shade, card)
    screen.set_clip(clip)
    border = theme.FOCUS if selected else theme.BORDER_SUBTLE
    pygame.draw.rect(screen, border, card, 3 if selected else 1, border_radius=theme.RADIUS_LG)
    if selected:
        draw_focus_ring(pygame, screen, card)
    title = _fit_surface(fonts["card"], game.descriptor.title, card.width - 78, theme.TEXT)
    screen.blit(title, (card.x + 14, card.bottom - 42))
    label = "2P" if game.descriptor.max_players >= 2 else "1P"
    draw_pill(
        pygame,
        screen,
        pygame.Rect(card.right - 52, card.bottom - 43, 38, 28),
        label,
        fonts["tiny"],
        (24, 62, 77),
        theme.FOCUS,
    )


def _draw_shelf(pygame, screen, context, rect, fonts, games, selected_index, hover_amounts):
    screen.blit(fonts["section"].render("Your Arcade", True, theme.TEXT), (rect.x, rect.y))
    counter = fonts["small"].render(f"{selected_index + 1} / {len(games)}", True, theme.MUTED)
    screen.blit(counter, (rect.right - counter.get_width(), rect.y + 5))
    cards = compute_shelf_cards(pygame, rect, len(games), selected_index)
    clip = screen.get_clip()
    screen.set_clip(pygame.Rect(rect.x - 4, rect.y + 34, rect.width + 8, rect.height - 30))
    for index, (card, game) in enumerate(zip(cards, games)):
        _draw_card(
            pygame,
            screen,
            context,
            card,
            fonts,
            game,
            index == selected_index,
            hover_amounts.get(game.descriptor.game_id, 0.0),
        )
    screen.set_clip(clip)
    return cards


def _draw_footer(pygame, screen, rect, font):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((9, 15, 22, 238))
    screen.blit(surface, rect)
    pygame.draw.line(screen, theme.BORDER_SUBTLE, (0, rect.y), (rect.width, rect.y))
    hint = "← →  Select     Enter  Play     I  Game info     S  Settings     Esc  Exit"
    rendered = _fit_surface(font, hint, rect.width - 48, theme.MUTED)
    screen.blit(rendered, rendered.get_rect(center=rect.center))


def _info_geometry(pygame, screen_size):
    width, height = screen_size
    panel = pygame.Rect(0, 0, min(720, width - 48), min(450, height - 96))
    panel.center = (width // 2, height // 2)
    play = pygame.Rect(panel.x + 30, panel.bottom - 76, 180, 46)
    close = pygame.Rect(panel.right - 150, panel.bottom - 76, 120, 46)
    return panel, play, close


def _draw_info(pygame, screen, fonts, game, panel, play_rect, close_rect):
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((2, 5, 9, 210))
    screen.blit(veil, (0, 0))
    _panel(pygame, screen, panel, (20, 30, 40), (79, 99, 116), theme.RADIUS_XL)
    descriptor = game.descriptor
    screen.blit(fonts["tiny"].render("GAME INFO", True, theme.FOCUS), (panel.x + 30, panel.y + 28))
    title = _fit_surface(fonts["modal"], descriptor.title, panel.width - 60, theme.TEXT)
    screen.blit(title, (panel.x + 30, panel.y + 56))
    y = panel.y + 112
    for line in _wrap_lines(fonts["body"], descriptor.short_description, panel.width - 60, 3):
        screen.blit(fonts["body"].render(line, True, (205, 215, 223)), (panel.x + 30, y))
        y += 28
    y += 16
    modes = ", ".join(value.replace("_", " ").title() for value in descriptor.supported_modes)
    for text in (
        f"Players: {_player_label(descriptor)}",
        f"Modes: {modes}",
        f"Category: {_primary_tag(descriptor)}",
        "Platform mode: local / offline first",
    ):
        screen.blit(fonts["body"].render(text, True, theme.MUTED), (panel.x + 30, y))
        y += 30
    mouse = pygame.mouse.get_pos()
    draw_button(
        pygame,
        screen,
        play_rect,
        "PLAY NOW",
        fonts["button"],
        color=theme.BRAND_PRIMARY,
        state=ButtonState(hovered=play_rect.collidepoint(mouse)),
    )
    draw_button(
        pygame,
        screen,
        close_rect,
        "CLOSE",
        fonts["button"],
        color=theme.PANEL_ALT,
        state=ButtonState(hovered=close_rect.collidepoint(mouse)),
    )


def run_arcade_shelf_scene(pygame, context, registry) -> SceneResult:
    """Run the product home and launch the selected registered mini-game."""

    screen = context.screen
    clock = context.clock
    fonts = {
        "top": context.assets.font(pygame, "display", 26, bold=True),
        "hero": context.assets.font(pygame, "display", 50, bold=True),
        "modal": context.assets.font(pygame, "display", 36, bold=True),
        "section": context.assets.font(pygame, "display", 24, bold=True),
        "card": context.assets.font(pygame, "body", 18, bold=True),
        "body": context.assets.font(pygame, "body", 18),
        "button": context.assets.font(pygame, "body", 16, bold=True),
        "small": context.assets.font(pygame, "body", 14),
        "small_bold": context.assets.font(pygame, "body", 14, bold=True),
        "tiny": context.assets.font(pygame, "body", 11, bold=True),
    }
    games = [game for game in registry.list_all() if game.descriptor.enabled]
    if not games:
        return SceneResult(PlatformAction.QUIT)

    selected = 0
    info_open = False
    pressed = None
    hover_amounts: dict[str, float] = {}
    while True:
        context.audio.update()
        layout = compute_arcade_shelf_layout(pygame, screen.get_size())
        game = games[selected]
        cards = compute_shelf_cards(pygame, layout.shelf, len(games), selected)
        play_rect = pygame.Rect(layout.hero.x + 46, layout.hero.bottom - 76, 176, 48)
        info_rect = pygame.Rect(play_rect.right + 14, play_rect.y, 154, 48)
        settings_rect = pygame.Rect(screen.get_width() - 132, 16, 108, 44)
        credits_rect = pygame.Rect(settings_rect.x - 104, 16, 94, 44)
        panel, overlay_play, overlay_close = _info_geometry(pygame, screen.get_size())
        mouse = pygame.mouse.get_pos()
        hovered = next((index for index, rect in enumerate(cards) if rect.collidepoint(mouse)), None)
        for index, item in enumerate(games):
            key = item.descriptor.game_id
            value = hover_amounts.get(key, 0.0)
            target = 1.0 if hovered == index else 0.0
            hover_amounts[key] = value + (target - value) * 0.24

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN:
                if info_open:
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        info_open = False
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                    continue
                if event.key == pygame.K_ESCAPE:
                    return SceneResult(PlatformAction.QUIT)
                if event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_TAB):
                    selected = (selected + 1) % len(games)
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % len(games)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                elif event.key == pygame.K_i:
                    info_open = True
                elif event.key == pygame.K_s:
                    return SceneResult(PlatformAction.SETTINGS)
                elif event.key == pygame.K_c:
                    return SceneResult(PlatformAction.ABOUT)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pressed = None
                if info_open:
                    if overlay_play.collidepoint(event.pos):
                        pressed = "overlay_play"
                    elif overlay_close.collidepoint(event.pos):
                        pressed = "overlay_close"
                    elif not panel.collidepoint(event.pos):
                        info_open = False
                    continue
                if play_rect.collidepoint(event.pos):
                    pressed = "play"
                elif info_rect.collidepoint(event.pos):
                    pressed = "info"
                elif settings_rect.collidepoint(event.pos):
                    pressed = "settings"
                elif credits_rect.collidepoint(event.pos):
                    pressed = "credits"
                else:
                    for index, rect in enumerate(cards):
                        if rect.collidepoint(event.pos):
                            pressed = ("card", index)
                            break
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                target = pressed
                pressed = None
                if target == "overlay_play" and overlay_play.collidepoint(event.pos):
                    return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                if target == "overlay_close" and overlay_close.collidepoint(event.pos):
                    info_open = False
                elif target == "play" and play_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                elif target == "info" and info_rect.collidepoint(event.pos):
                    info_open = True
                elif target == "settings" and settings_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.SETTINGS)
                elif target == "credits" and credits_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.ABOUT)
                elif isinstance(target, tuple) and target[0] == "card":
                    index = target[1]
                    if cards[index].collidepoint(event.pos):
                        selected = index

        game = games[selected]
        _draw_background(pygame, screen, context, game.descriptor)
        _draw_top_bar(pygame, screen, context, layout.top_bar, fonts, settings_rect, credits_rect)
        _draw_hero(pygame, screen, context, layout.hero, fonts, game, play_rect, info_rect)
        _draw_shelf(pygame, screen, context, layout.shelf, fonts, games, selected, hover_amounts)
        _draw_footer(pygame, screen, layout.footer, fonts["small"])
        if info_open:
            _draw_info(pygame, screen, fonts, game, panel, overlay_play, overlay_close)
        pygame.display.flip()
        clock.tick(60)
