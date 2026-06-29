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
    content_height = max(320, footer.top - margin - (top_bar.bottom + margin))
    shelf_height = max(SHELF_MIN_HEIGHT, min(238, int(content_height * 0.34)))
    hero = pygame.Rect(
        margin,
        top_bar.bottom + margin,
        width - margin * 2,
        max(210, content_height - shelf_height - margin),
    )
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
        start_x = max(
            shelf_rect.right - total_width,
            min(shelf_rect.x, shelf_rect.centerx - selected_center),
        )
    return [
        pygame.Rect(start_x + index * (card_width + gap), shelf_rect.y + 40, card_width, card_height)
        for index in range(count)
    ]


def _fit(font, text: str, max_width: int, color):
    label = text
    surface = font.render(label, True, color)
    while surface.get_width() > max_width and len(label) > 4:
        label = f"{label[:-4].rstrip()}..."
        surface = font.render(label, True, color)
    return surface


def _wrap(font, text: str, max_width: int, max_lines: int = 2) -> list[str]:
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = word if not current else f"{current} {word}"
        if font.size(candidate)[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
            if len(lines) == max_lines:
                break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and " ".join(lines) != text:
        value = f"{lines[-1]}..."
        while font.size(value)[0] > max_width and len(value) > 4:
            value = f"{value[:-4].rstrip()}..."
        lines[-1] = value
    return lines


def _players(descriptor) -> str:
    if descriptor.min_players == descriptor.max_players:
        suffix = "s" if descriptor.max_players != 1 else ""
        return f"{descriptor.max_players} Player{suffix}"
    return f"{descriptor.min_players}-{descriptor.max_players} Players"


def _category(descriptor) -> str:
    ignored = {"single-player", "1v1", "ai", "local", "turn-based"}
    tag = next((value for value in descriptor.tags if value not in ignored), "mini-game")
    return tag.replace("-", " ").title()


def _verified(descriptor) -> bool:
    capabilities = {
        GameCapability.ONLINE_MULTIPLAYER,
        GameCapability.CONFIDENTIAL_MATCH,
        GameCapability.VERIFIED_RESULT,
    }
    return any(value in capabilities for value in descriptor.capabilities)


def _button(pygame, screen, rect, label, font, color, focused=False):
    mouse = pygame.mouse.get_pos()
    draw_button(
        pygame,
        screen,
        rect,
        label,
        font,
        color=color,
        state=ButtonState(hovered=rect.collidepoint(mouse), focused=focused),
    )


def _draw_background(pygame, screen, context, descriptor):
    artwork = context.assets.cover_image(
        pygame,
        descriptor.thumbnail,
        screen.get_size(),
        focal=(0.5, 0.45),
    )
    screen.blit(artwork, (0, 0))
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
    _button(pygame, screen, credits_rect, "Credits", fonts["small_bold"], theme.PANEL_ALT)
    _button(pygame, screen, settings_rect, "Settings", fonts["small_bold"], theme.PANEL_ALT)


def _draw_hero(pygame, screen, context, rect, fonts, game, play_rect, info_rect):
    descriptor = game.descriptor
    pygame.draw.rect(screen, (2, 5, 9), rect.move(0, 8), border_radius=theme.RADIUS_XL)
    artwork = context.assets.cover_image(pygame, descriptor.thumbnail, rect.size, focal=(0.62, 0.48))
    previous_clip = screen.get_clip()
    screen.set_clip(rect)
    screen.blit(artwork, rect)
    gradient = pygame.Surface(rect.size, pygame.SRCALPHA)
    for index in range(16):
        ratio = index / 15
        alpha = int(240 * (1 - ratio) ** 1.55)
        pygame.draw.rect(
            gradient,
            (6, 11, 18, alpha),
            (int(rect.width * ratio * 0.84), 0, rect.width // 15 + 6, rect.height),
        )
    pygame.draw.rect(gradient, (4, 8, 13, 105), (0, rect.height - 110, rect.width, 110))
    screen.blit(gradient, rect)
    screen.set_clip(previous_clip)
    pygame.draw.rect(screen, (83, 104, 121), rect, 1, border_radius=theme.RADIUS_XL)

    left = rect.x + max(28, min(58, rect.width // 24))
    top = rect.y + max(24, int(rect.height * 0.11))
    max_width = min(610, int(rect.width * 0.58))
    screen.blit(fonts["tiny"].render("FEATURED IN YOUR ARCADE", True, theme.FOCUS), (left, top))
    title = _fit(fonts["hero"], descriptor.title, max_width, theme.TEXT)
    screen.blit(title, (left, top + 28))
    y = top + title.get_height() + 40
    for line in _wrap(fonts["body"], descriptor.short_description, max_width, 1 if rect.height < 300 else 2):
        screen.blit(fonts["body"].render(line, True, (211, 220, 227)), (left, y))
        y += 27
    y += 8
    x = left
    for label, fill in (
        (_players(descriptor), theme.BLUE),
        (_category(descriptor), (75, 91, 108)),
        ("Offline", (53, 116, 76)),
    ):
        width = max(74, fonts["small_bold"].size(label)[0] + 28)
        draw_pill(pygame, screen, pygame.Rect(x, y, width, 32), label, fonts["small_bold"], fill)
        x += width + 10
    if _verified(descriptor) and rect.height >= 340:
        note = fonts["small"].render("Verified mode is available from this game's setup flow.", True, theme.MUTED)
        screen.blit(note, (left, y + 42))
    _button(pygame, screen, play_rect, "PLAY NOW", fonts["button"], theme.BRAND_PRIMARY, focused=True)
    _button(pygame, screen, info_rect, "GAME INFO", fonts["button"], theme.PANEL_ALT)


def _draw_card(pygame, screen, context, rect, fonts, game, selected, hover):
    card = rect.move(0, -int(7 * max(hover, 1.0 if selected else 0.0)))
    pygame.draw.rect(screen, (2, 5, 9), card.move(0, 7), border_radius=theme.RADIUS_LG)
    artwork = context.assets.cover_image(pygame, game.descriptor.thumbnail, card.size)
    previous_clip = screen.get_clip()
    screen.set_clip(card)
    screen.blit(artwork, card)
    shade = pygame.Surface(card.size, pygame.SRCALPHA)
    shade.fill((6, 10, 16, 30 if selected else 86))
    pygame.draw.rect(shade, (4, 8, 13, 205), (0, card.height - 54, card.width, 54))
    screen.blit(shade, card)
    screen.set_clip(previous_clip)
    pygame.draw.rect(
        screen,
        theme.FOCUS if selected else theme.BORDER_SUBTLE,
        card,
        3 if selected else 1,
        border_radius=theme.RADIUS_LG,
    )
    if selected:
        draw_focus_ring(pygame, screen, card)
    title = _fit(fonts["card"], game.descriptor.title, card.width - 78, theme.TEXT)
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


def _draw_shelf(pygame, screen, context, rect, fonts, games, selected, hover_amounts):
    screen.blit(fonts["section"].render("Your Arcade", True, theme.TEXT), (rect.x, rect.y))
    counter = fonts["small"].render(f"{selected + 1} / {len(games)}", True, theme.MUTED)
    screen.blit(counter, (rect.right - counter.get_width(), rect.y + 5))
    cards = compute_shelf_cards(pygame, rect, len(games), selected)
    previous_clip = screen.get_clip()
    screen.set_clip(pygame.Rect(rect.x - 4, rect.y + 34, rect.width + 8, rect.height - 30))
    for index, (card, game) in enumerate(zip(cards, games)):
        _draw_card(
            pygame,
            screen,
            context,
            card,
            fonts,
            game,
            index == selected,
            hover_amounts.get(game.descriptor.game_id, 0.0),
        )
    screen.set_clip(previous_clip)
    return cards


def _draw_footer(pygame, screen, rect, font):
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((9, 15, 22, 238))
    screen.blit(surface, rect)
    pygame.draw.line(screen, theme.BORDER_SUBTLE, (0, rect.y), (rect.width, rect.y))
    hint = "← →  Select     Enter  Play     I  Game info     S  Settings     Esc  Exit"
    rendered = _fit(font, hint, rect.width - 48, theme.MUTED)
    screen.blit(rendered, rendered.get_rect(center=rect.center))


def _info_rects(pygame, screen_size):
    width, height = screen_size
    panel = pygame.Rect(0, 0, min(720, width - 48), min(450, height - 96))
    panel.center = (width // 2, height // 2)
    return (
        panel,
        pygame.Rect(panel.x + 30, panel.bottom - 76, 180, 46),
        pygame.Rect(panel.right - 150, panel.bottom - 76, 120, 46),
    )


def _draw_info(pygame, screen, fonts, game, panel, play_rect, close_rect):
    veil = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    veil.fill((2, 5, 9, 210))
    screen.blit(veil, (0, 0))
    pygame.draw.rect(screen, (20, 30, 40), panel, border_radius=theme.RADIUS_XL)
    pygame.draw.rect(screen, (79, 99, 116), panel, 1, border_radius=theme.RADIUS_XL)
    descriptor = game.descriptor
    screen.blit(fonts["tiny"].render("GAME INFO", True, theme.FOCUS), (panel.x + 30, panel.y + 28))
    title = _fit(fonts["modal"], descriptor.title, panel.width - 60, theme.TEXT)
    screen.blit(title, (panel.x + 30, panel.y + 56))
    y = panel.y + 112
    for line in _wrap(fonts["body"], descriptor.short_description, panel.width - 60, 3):
        screen.blit(fonts["body"].render(line, True, (205, 215, 223)), (panel.x + 30, y))
        y += 28
    y += 16
    modes = ", ".join(value.replace("_", " ").title() for value in descriptor.supported_modes)
    for text in (
        f"Players: {_players(descriptor)}",
        f"Modes: {modes}",
        f"Category: {_category(descriptor)}",
        "Platform mode: local / offline first",
    ):
        screen.blit(fonts["body"].render(text, True, theme.MUTED), (panel.x + 30, y))
        y += 30
    _button(pygame, screen, play_rect, "PLAY NOW", fonts["button"], theme.BRAND_PRIMARY)
    _button(pygame, screen, close_rect, "CLOSE", fonts["button"], theme.PANEL_ALT)


def _fonts(context, pygame):
    return {
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


def run_arcade_shelf_scene(pygame, context, registry) -> SceneResult:
    """Run the product home and launch the selected registered mini-game."""
    screen, clock, fonts = context.screen, context.clock, _fonts(context, pygame)
    games = [game for game in registry.list_all() if game.descriptor.enabled]
    if not games:
        return SceneResult(PlatformAction.QUIT)
    selected, info_open, pressed = 0, False, None
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
        panel, modal_play, modal_close = _info_rects(pygame, screen.get_size())
        mouse = pygame.mouse.get_pos()
        hovered = next((index for index, rect in enumerate(cards) if rect.collidepoint(mouse)), None)
        for index, item in enumerate(games):
            key = item.descriptor.game_id
            current = hover_amounts.get(key, 0.0)
            hover_amounts[key] = current + ((1.0 if hovered == index else 0.0) - current) * 0.24

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
                    if modal_play.collidepoint(event.pos):
                        pressed = "modal_play"
                    elif modal_close.collidepoint(event.pos):
                        pressed = "modal_close"
                    elif not panel.collidepoint(event.pos):
                        info_open = False
                    continue
                targets = (
                    ("play", play_rect),
                    ("info", info_rect),
                    ("settings", settings_rect),
                    ("credits", credits_rect),
                )
                pressed = next((name for name, rect in targets if rect.collidepoint(event.pos)), None)
                if pressed is None:
                    pressed = next(
                        (("card", index) for index, rect in enumerate(cards) if rect.collidepoint(event.pos)), None
                    )
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                target, pressed = pressed, None
                if target == "modal_play" and modal_play.collidepoint(event.pos):
                    return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                if target == "modal_close" and modal_close.collidepoint(event.pos):
                    info_open = False
                elif target == "play" and play_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
                elif target == "info" and info_rect.collidepoint(event.pos):
                    info_open = True
                elif target == "settings" and settings_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.SETTINGS)
                elif target == "credits" and credits_rect.collidepoint(event.pos):
                    return SceneResult(PlatformAction.ABOUT)
                elif isinstance(target, tuple) and cards[target[1]].collidepoint(event.pos):
                    selected = target[1]

        game = games[selected]
        _draw_background(pygame, screen, context, game.descriptor)
        _draw_top_bar(pygame, screen, context, layout.top_bar, fonts, settings_rect, credits_rect)
        _draw_hero(pygame, screen, context, layout.hero, fonts, game, play_rect, info_rect)
        _draw_shelf(pygame, screen, context, layout.shelf, fonts, games, selected, hover_amounts)
        _draw_footer(pygame, screen, layout.footer, fonts["small"])
        if info_open:
            _draw_info(pygame, screen, fonts, game, panel, modal_play, modal_close)
        pygame.display.flip()
        clock.tick(60)
