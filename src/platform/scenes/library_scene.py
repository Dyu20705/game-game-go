"""Desktop-first game hub scene driven by GameRegistry."""

import random
from dataclasses import dataclass
from datetime import date

from src.platform.blockchain.domain.network import ChainHealthStatus
from src.platform.games import GameCapability
from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text
from src.platform.ui.icons import draw_fallback_icon

TOP_NAV_HEIGHT = 78
SIDEBAR_WIDTH = 224
RIGHT_PANEL_WIDTH = 288
TOURNAMENT_DOCK_HEIGHT = 80
CONTENT_GAP = theme.SPACE_6
CARD_MIN_HEIGHT = 284
CARD_MAX_WIDTH = 340

MODE_ALL = "all"
MODE_SINGLE = "single-player"
MODE_TWO = "two-player"

SIDEBAR_GROUPS = (
    ("Discover", (("all", "All Games"),)),
    ("Categories", (("strategy", "Strategy"), ("puzzle", "Puzzle"), ("quick", "Quick Play"), ("on-chain", "On-chain"))),
    ("Library", (("favorites", "Favorites"),)),
)


@dataclass(frozen=True)
class HubLayout:
    top_nav: object
    sidebar: object
    main: object
    right_panel: object | None
    tournament: object


def compute_hub_layout(pygame, screen_size) -> HubLayout:
    """Compute the responsive desktop hub layout."""

    width, height = screen_size
    top_nav = pygame.Rect(0, 0, width, TOP_NAV_HEIGHT)
    tournament = pygame.Rect(0, height - TOURNAMENT_DOCK_HEIGHT, width, TOURNAMENT_DOCK_HEIGHT)
    content_top = TOP_NAV_HEIGHT + CONTENT_GAP
    content_height = max(280, height - TOP_NAV_HEIGHT - TOURNAMENT_DOCK_HEIGHT - CONTENT_GAP * 2)

    if width >= 1180:
        sidebar_width = SIDEBAR_WIDTH
        right_width = RIGHT_PANEL_WIDTH if width >= 1600 else 0
        sidebar = pygame.Rect(CONTENT_GAP, content_top, sidebar_width, content_height)
        main_x = sidebar.right + CONTENT_GAP
        right_panel = (
            pygame.Rect(width - right_width - CONTENT_GAP, content_top, right_width, content_height)
            if right_width
            else None
        )
        main_right = right_panel.left - CONTENT_GAP if right_panel else width - CONTENT_GAP
        main = pygame.Rect(main_x, content_top, max(360, main_right - main_x), content_height)
    else:
        sidebar = pygame.Rect(CONTENT_GAP, content_top, 0, 0)
        right_panel = None
        main = pygame.Rect(CONTENT_GAP, content_top, width - CONTENT_GAP * 2, content_height)
    return HubLayout(top_nav, sidebar, main, right_panel, tournament)


def grid_columns(width: int) -> int:
    """Return card columns for the game grid at a given content width."""

    if width >= 1240:
        return 4
    if width >= 980:
        return 3
    if width >= 640:
        return 2
    return 1


def game_mode(descriptor) -> str:
    return MODE_TWO if descriptor.max_players >= 2 and descriptor.min_players >= 2 else MODE_SINGLE


def settlement_mode(descriptor) -> str:
    on_chain_caps = {
        GameCapability.ONLINE_MULTIPLAYER,
        GameCapability.CONFIDENTIAL_MATCH,
        GameCapability.VERIFIED_RESULT,
        GameCapability.OASIS_IDENTITY,
        GameCapability.PLATFORM_ACHIEVEMENT,
    }
    return "hybrid" if any(capability in on_chain_caps for capability in descriptor.capabilities) else "off-chain"


def entry_fee_label(_descriptor) -> str:
    """Return the fee label shown on cards without inventing token costs."""

    return "Free"


def wallet_requirement_label(descriptor) -> str:
    """Summarize wallet needs for progressive disclosure UI."""

    if settlement_mode(descriptor) == "off-chain":
        return "Wallet not required to play"
    return "Wallet only required before on-chain actions"


def eligible_tournament_games(games):
    """Return real registered games that can participate in a local 2P tournament."""

    return [game for game in games if game.descriptor.enabled and game.descriptor.max_players >= 2]


def select_tournament_games(games, limit: int = 7):
    selected = eligible_tournament_games(games)
    random.shuffle(selected)
    return selected[:limit]


def daily_challenge_title(games, today: date | None = None) -> str:
    enabled = [game for game in games if game.descriptor.enabled]
    if not enabled:
        return "Random game"
    day = today or date.today()
    index = day.toordinal() % len(enabled)
    return enabled[index].descriptor.title


def filter_games(games, selected_filter: str, selected_mode: str = MODE_ALL, search_query: str = ""):
    """Filter by one category, one player mode, and an optional search query."""

    filtered = list(games)
    if selected_filter == "on-chain":
        filtered = [game for game in filtered if settlement_mode(game.descriptor) != "off-chain"]
    elif selected_filter == "quick":
        filtered = [game for game in filtered if game.descriptor.max_players == 1 or "arcade" in game.descriptor.tags]
    elif selected_filter == "favorites":
        filtered = []
    elif selected_filter != MODE_ALL:
        filtered = [game for game in filtered if selected_filter in game.descriptor.tags]

    if selected_mode == MODE_SINGLE:
        filtered = [game for game in filtered if game_mode(game.descriptor) == MODE_SINGLE]
    elif selected_mode == MODE_TWO:
        filtered = [game for game in filtered if game.descriptor.max_players >= 2]

    query = search_query.strip().lower()
    if query:
        filtered = [
            game
            for game in filtered
            if query in game.descriptor.title.lower()
            or query in game.descriptor.short_description.lower()
            or any(query in tag.lower() for tag in game.descriptor.tags)
        ]
    return filtered


def wallet_summary(context) -> dict[str, str]:
    """Describe the available wallet/network state without faking balances."""

    blockchain = getattr(context, "blockchain", None)
    if blockchain is None:
        return {
            "status": "disconnected",
            "network": "Oasis Sapphire",
            "balance": "---- ROSE",
            "detail": "Wallet provider unavailable",
        }

    config = getattr(blockchain, "config", None)
    health = blockchain.health()
    network = "Oasis Sapphire"
    if config and getattr(config, "mode", None):
        network = (
            "Oasis Sapphire" if config.mode.value == "oasis_testnet" else config.mode.value.replace("_", " ").title()
        )

    if health.mode == "local":
        status = "connected"
        detail = "Local dev identity"
    elif health.sapphire == ChainHealthStatus.CONNECTED:
        status = "connected"
        detail = "Sapphire RPC configured"
    elif health.mode == "offline":
        status = "disconnected"
        detail = "Offline mode"
    else:
        status = "wrong-network"
        detail = "Sapphire config incomplete"

    return {
        "status": status,
        "network": network,
        "balance": "---- ROSE",
        "detail": detail,
    }


def _fit_text(pygame, font, text, max_width, color):
    label = text
    surface = font.render(label, True, color)
    while surface.get_width() > max_width and len(label) > 4:
        label = label[:-4].rstrip() + "..."
        surface = font.render(label, True, color)
    return surface


def _draw_panel(pygame, screen, rect, fill=theme.PANEL, border=theme.BORDER_SUBTLE, radius=theme.RADIUS_LG):
    pygame.draw.rect(screen, fill, rect, border_radius=radius)
    pygame.draw.rect(screen, border, rect, 1, border_radius=radius)


def _draw_pill(pygame, screen, rect, label, font, fill, color=theme.TEXT, border=None):
    pygame.draw.rect(screen, fill, rect, border_radius=rect.height // 2)
    if border:
        pygame.draw.rect(screen, border, rect, 1, border_radius=rect.height // 2)
    surface = _fit_text(pygame, font, label, rect.width - 18, color)
    screen.blit(surface, surface.get_rect(center=rect.center))


def _draw_settings_icon(pygame, screen, rect, color):
    center = rect.center
    for dx, dy in ((0, -12), (0, 12), (-12, 0), (12, 0), (-8, -8), (8, -8), (-8, 8), (8, 8)):
        pygame.draw.circle(screen, color, (center[0] + dx, center[1] + dy), 3)
    pygame.draw.circle(screen, color, center, 11, 2)
    pygame.draw.circle(screen, color, center, 4)


def _draw_focus_ring(pygame, screen, rect):
    pygame.draw.rect(screen, (96, 220, 240), rect.inflate(6, 6), 3, border_radius=theme.RADIUS_XL)


def _draw_truncated_text(pygame, screen, font, text, pos, max_width, color):
    surface = _fit_text(pygame, font, text, max_width, color)
    screen.blit(surface, pos)
    return surface


def _draw_top_nav(pygame, screen, rect, fonts, wallet):
    pygame.draw.rect(screen, (228, 244, 249), rect)
    pygame.draw.line(screen, (188, 218, 228), (0, rect.bottom - 1), (rect.width, rect.bottom - 1), 1)

    logo = pygame.Rect(18 if rect.width < 760 else 24, 15, 48, 48)
    pygame.draw.rect(screen, (89, 115, 132), logo, border_radius=14)
    pygame.draw.circle(screen, theme.AMBER, logo.center, 13)
    pygame.draw.circle(screen, theme.DANGER, logo.center, 5)

    title_font = fonts["body_bold"] if rect.width < 760 else fonts["title"]
    title = title_font.render("Game Game Go", True, (55, 62, 75))
    screen.blit(title, (logo.right + 12, 24 if rect.width < 760 else 18))

    if rect.width >= 1120:
        nav_items = ("Home", "Games", "Leaderboard", "Rewards")
        right_reserved = 430 if wallet["status"] == "connected" else 310
        x = max(360, min(430, rect.width // 3))
        max_nav_right = rect.width - right_reserved
        for item in nav_items:
            color = (255, 86, 80) if item == "Games" else (55, 62, 75)
            surface = fonts["body_bold"].render(item, True, color)
            item_rect = pygame.Rect(x - 12, 17, surface.get_width() + 24, 44)
            if item_rect.right > max_nav_right:
                break
            fill = (255, 255, 255) if item == "Games" else (0, 0, 0)
            if item == "Games":
                pygame.draw.rect(screen, fill, item_rect, border_radius=theme.RADIUS_PILL)
            screen.blit(surface, surface.get_rect(center=item_rect.center))
            x = item_rect.right + 6

    right = rect.width - 24
    if rect.width >= 760:
        settings = pygame.Rect(right - 44, 17, 44, 44)
        pygame.draw.rect(screen, (119, 143, 159), settings, border_radius=theme.RADIUS_MD)
        pygame.draw.rect(screen, (88, 110, 124), settings, 1, border_radius=theme.RADIUS_MD)
        _draw_settings_icon(pygame, screen, settings, (255, 255, 255))
        right = settings.left - 10
    wallet_label = "Connect Wallet" if wallet["status"] == "disconnected" else "Guest Local"
    wallet_width = 150 if rect.width >= 760 else 104
    wallet_rect = pygame.Rect(right - wallet_width, 18, wallet_width, 42)
    wallet_fill = theme.DANGER if wallet["status"] == "disconnected" else theme.ACCENT
    _draw_pill(pygame, screen, wallet_rect, wallet_label, fonts["small_bold"], wallet_fill, (255, 255, 255))
    if rect.width >= 900 and wallet["status"] != "disconnected":
        right = wallet_rect.left - 10
        _draw_pill(
            pygame,
            screen,
            pygame.Rect(right - 96, 18, 96, 42),
            wallet["balance"],
            fonts["small_bold"],
            (255, 255, 255),
            (55, 62, 75),
            (188, 218, 228),
        )
        right -= 106
        _draw_pill(
            pygame,
            screen,
            pygame.Rect(right - 124, 18, 124, 42),
            "Sapphire",
            fonts["small_bold"],
            theme.BLUE,
            (255, 255, 255),
        )
    elif rect.width >= 900:
        right = wallet_rect.left - 10
        _draw_pill(
            pygame,
            screen,
            pygame.Rect(right - 118, 18, 118, 42),
            "---- ROSE",
            fonts["small_bold"],
            (255, 255, 255),
            (55, 62, 75),
            (188, 218, 228),
        )


def _top_nav_targets(pygame, width, wallet, nav_font):
    right = width - 24
    targets = {}
    if width >= 760:
        settings = pygame.Rect(right - 44, 17, 44, 44)
        targets["settings"] = settings
        right = settings.left - 10
    wallet_width = 150 if width >= 760 else 104
    wallet_rect = pygame.Rect(right - wallet_width, 18, wallet_width, 42)
    targets["wallet"] = wallet_rect
    if width >= 1120:
        nav_items = (("home", "Home"), ("games", "Games"), ("leaderboard", "Leaderboard"), ("rewards", "Rewards"))
        right_reserved = 430 if wallet["status"] == "connected" else 310
        x = max(360, min(430, width // 3))
        max_nav_right = width - right_reserved
        for key, item in nav_items:
            surface = nav_font.render(item, True, (55, 62, 75))
            item_rect = pygame.Rect(x - 12, 17, surface.get_width() + 24, 44)
            if item_rect.right > max_nav_right:
                break
            targets[key] = item_rect
            x = item_rect.right + 6
    return targets


def _draw_sidebar(pygame, screen, rect, fonts, selected_filter, daily_game_title="Random game"):
    if rect.width <= 0:
        return []
    _draw_panel(pygame, screen, rect, theme.SIDEBAR, theme.BORDER_SUBTLE)
    y = rect.y + theme.SPACE_5
    clickable = []
    for group, items in SIDEBAR_GROUPS:
        screen.blit(fonts["tiny_bold"].render(group.upper(), True, theme.SUBTLE), (rect.x + theme.SPACE_5, y))
        y += theme.SPACE_6
        for key, label in items:
            item = pygame.Rect(rect.x + theme.SPACE_3, y, rect.width - theme.SPACE_6, 44)
            selected = key == selected_filter
            fill = (53, 66, 79) if selected else theme.SIDEBAR
            text_color = theme.TEXT if selected else theme.MUTED
            pygame.draw.rect(screen, fill, item, border_radius=theme.RADIUS_MD)
            if selected:
                pygame.draw.rect(
                    screen,
                    theme.BLUE,
                    pygame.Rect(item.x, item.y + 9, 4, item.height - 18),
                    border_radius=theme.RADIUS_PILL,
                )
            icon = pygame.Rect(item.x + 14, item.y + 13, 18, 18)
            pygame.draw.rect(screen, theme.RAISED if selected else theme.PANEL, icon, border_radius=theme.RADIUS_SM)
            surface = fonts["body"].render(label, True, text_color)
            screen.blit(surface, (item.x + 42, item.y + 11))
            clickable.append((item, key))
            y += 46
        y += theme.SPACE_3

    footer = pygame.Rect(rect.x + theme.SPACE_3, rect.bottom - 112, rect.width - theme.SPACE_6, 92)
    pygame.draw.rect(screen, (228, 244, 249), footer, border_radius=theme.RADIUS_MD)
    pygame.draw.rect(screen, (188, 218, 228), footer, 1, border_radius=theme.RADIUS_MD)
    screen.blit(fonts["small_bold"].render("Daily Challenge", True, (55, 62, 75)), (footer.x + 14, footer.y + 12))
    _draw_truncated_text(
        pygame,
        screen,
        fonts["small"],
        daily_game_title,
        (footer.x + 14, footer.y + 38),
        footer.width - 28,
        (76, 98, 111),
    )
    screen.blit(fonts["small"].render("Daily streak: 3", True, (76, 98, 111)), (footer.x + 14, footer.y + 64))
    return clickable


def _draw_mode_tabs(pygame, screen, rect, fonts, selected_filter):
    tabs = []
    labels = ((MODE_ALL, "All"), (MODE_SINGLE, "1 Player"), (MODE_TWO, "2 Players"))
    tab_width = min(120, (rect.width - theme.SPACE_2 * 2) // 3)
    for index, (key, label) in enumerate(labels):
        tab = pygame.Rect(rect.x + index * (tab_width + theme.SPACE_2), rect.y, tab_width, 44)
        selected = key == selected_filter
        fill = theme.BLUE if selected else theme.PANEL
        color = (255, 255, 255) if selected else theme.MUTED
        pygame.draw.rect(screen, fill, tab, border_radius=theme.RADIUS_MD)
        pygame.draw.rect(screen, theme.BORDER_SUBTLE, tab, 1, border_radius=theme.RADIUS_MD)
        surface = fonts["body_bold"].render(label, True, color)
        screen.blit(surface, surface.get_rect(center=tab.center))
        tabs.append((tab, key))
    return tabs


def _draw_artwork(pygame, screen, rect, descriptor, asset_service=None):
    if asset_service is not None:
        image = asset_service.scaled_image(pygame, descriptor.thumbnail, rect.size)
        previous_clip = screen.get_clip()
        screen.set_clip(rect)
        screen.blit(image, rect)
        screen.set_clip(previous_clip)
        return

    palette = {
        "color_wars": ((255, 87, 80), (29, 190, 222), (255, 207, 43)),
        "square_xo": ((74, 108, 255), (75, 212, 114), (255, 207, 43)),
        "demo_game": ((255, 89, 142), (29, 190, 222), (255, 255, 255)),
        "nuts_and_bolts": ((232, 228, 218), (105, 108, 112), (255, 193, 65)),
    }
    c1, c2, c3 = palette.get(descriptor.game_id, (theme.DANGER, theme.BLUE, theme.AMBER))
    previous_clip = screen.get_clip()
    screen.set_clip(rect)
    pygame.draw.rect(screen, c1, rect, border_radius=theme.RADIUS_LG)
    if descriptor.game_id == "square_xo":
        cell = max(24, rect.width // 4)
        for row in range(4):
            for col in range(4):
                tile = pygame.Rect(rect.x + col * cell + 8, rect.y + row * (cell // 2) + 12, cell - 12, cell // 2 + 18)
                pygame.draw.rect(screen, c2 if (row + col) % 2 else c3, tile, border_radius=theme.RADIUS_SM)
    elif descriptor.game_id == "demo_game":
        for index in range(5):
            center = (rect.x + 34 + index * max(34, rect.width // 6), rect.y + 34 + (index % 2) * 34)
            pygame.draw.circle(screen, c2, center, 22)
            pygame.draw.circle(screen, c3, center, 9)
    else:
        for index in range(4):
            x = rect.x + 38 + index * max(42, rect.width // 5)
            pygame.draw.circle(screen, c2 if index % 2 else c3, (x, rect.y + 40), 24)
            pygame.draw.rect(
                screen, c2 if index % 2 else c3, pygame.Rect(x - 12, rect.y + 66, 24, 48), border_radius=theme.RADIUS_SM
            )
    screen.set_clip(previous_clip)


def _draw_game_card(pygame, screen, rect, fonts, game, hover_amount=0.0, focused=False, asset_service=None):
    descriptor = game.descriptor
    interactive_amount = max(hover_amount, 1.0 if focused else 0.0)
    lift = int(-5 * interactive_amount)
    card = rect.move(0, lift)
    shadow = card.move(0, 7 + int(3 * interactive_amount))
    shadow_color = (7, 10, 14) if interactive_amount < 0.5 else (4, 8, 12)
    pygame.draw.rect(screen, shadow_color, shadow, border_radius=theme.RADIUS_XL)
    pygame.draw.rect(screen, theme.HOVER if interactive_amount else theme.PANEL, card, border_radius=theme.RADIUS_XL)
    pygame.draw.rect(
        screen, theme.BORDER if interactive_amount else theme.BORDER_SUBTLE, card, 2, border_radius=theme.RADIUS_XL
    )
    if focused:
        _draw_focus_ring(pygame, screen, card)

    padding = theme.SPACE_4
    art = pygame.Rect(
        card.x + padding, card.y + padding, card.width - padding * 2, int((card.width - padding * 2) * 9 / 16)
    )
    art.height = min(art.height, 142)
    _draw_artwork(pygame, screen, art, descriptor, asset_service)
    pygame.draw.rect(screen, (255, 255, 255), art, 1, border_radius=theme.RADIUS_LG)

    if descriptor.sort_order <= 15:
        badge = pygame.Rect(art.right - 64, art.y + 10, 52, 26)
        _draw_pill(pygame, screen, badge, "NEW", fonts["tiny_bold"], (24, 117, 137), theme.AMBER, (19, 24, 30))

    body_y = art.bottom + theme.SPACE_5
    title_surface = _fit_text(pygame, fonts["card_title"], descriptor.title, card.width - padding * 2, theme.TEXT)
    screen.blit(title_surface, (card.x + padding, body_y))

    mode_label = "2P" if descriptor.max_players >= 2 else "1P"
    fee_label = entry_fee_label(descriptor)
    footer_y = card.bottom - 54
    _draw_pill(
        pygame, screen, pygame.Rect(card.x + padding, footer_y + 6, 48, 32), mode_label, fonts["small_bold"], theme.BLUE
    )
    _draw_pill(
        pygame,
        screen,
        pygame.Rect(card.x + padding + 56, footer_y + 6, 72, 32),
        fee_label,
        fonts["small_bold"],
        (236, 246, 239),
        (39, 91, 53),
        (176, 218, 187),
    )
    play = pygame.Rect(card.right - padding - 82, footer_y, 82, 44)
    play_color = theme.BRAND_PRIMARY_HOVER if interactive_amount else theme.BRAND_PRIMARY
    draw_button(pygame, screen, play, "Play", fonts["small_bold"], color=play_color, text_color=(255, 255, 255))
    return card


def _draw_game_detail_strip(pygame, screen, rect, fonts, game):
    descriptor = game.descriptor
    _draw_panel(pygame, screen, rect, theme.PANEL, theme.BORDER_SUBTLE, theme.RADIUS_MD)
    x = rect.x + theme.SPACE_4
    mode_label = "2 Players" if descriptor.max_players >= 2 else "1 Player"
    summary = f"{descriptor.title}  |  {mode_label}"
    _draw_truncated_text(
        pygame, screen, fonts["small_bold"], summary, (x, rect.y + 12), rect.width - 220, (205, 216, 225)
    )
    settlement = settlement_mode(descriptor).replace("-", " ").title()
    _draw_pill(
        pygame,
        screen,
        pygame.Rect(rect.right - 190, rect.y + 7, 82, 30),
        settlement,
        fonts["tiny_bold"],
        theme.RAISED,
        theme.TEXT,
        theme.BORDER_SUBTLE,
    )
    _draw_pill(
        pygame,
        screen,
        pygame.Rect(rect.right - 100, rect.y + 7, 84, 30),
        entry_fee_label(descriptor),
        fonts["tiny_bold"],
        (236, 246, 239),
        (39, 91, 53),
        (176, 218, 187),
    )


def _draw_search_box(pygame, screen, rect, fonts, search_query, search_active):
    fill = theme.HOVER if search_active else theme.PANEL
    border = theme.BRAND_PRIMARY if search_active else theme.BORDER_SUBTLE
    pygame.draw.rect(screen, fill, rect, border_radius=theme.RADIUS_MD)
    pygame.draw.rect(screen, border, rect, 2 if search_active else 1, border_radius=theme.RADIUS_MD)
    label = search_query if search_query else "Search games"
    color = theme.TEXT if search_query else theme.MUTED
    _draw_truncated_text(pygame, screen, fonts["small"], label, (rect.x + 16, rect.y + 13), rect.width - 54, color)
    if search_query:
        clear = pygame.Rect(rect.right - 36, rect.y + 8, 28, 28)
        pygame.draw.rect(screen, theme.RAISED, clear, border_radius=theme.RADIUS_SM)
        marker = fonts["small_bold"].render("x", True, theme.TEXT)
        screen.blit(marker, marker.get_rect(center=clear.center))
    elif search_active:
        cursor = pygame.Rect(rect.x + 104, rect.y + 13, 2, 18)
        pygame.draw.rect(screen, theme.BRAND_PRIMARY, cursor)


def _draw_game_browser(
    pygame,
    screen,
    rect,
    fonts,
    games,
    selected_filter,
    selected_mode,
    search_query,
    search_active,
    mouse_pos,
    focused_index,
    hover_amounts,
    control_panel=None,
    asset_service=None,
):
    title = fonts["heading"].render("Choose Your Challenge", True, theme.TEXT)
    screen.blit(title, (rect.x, rect.y))
    subtitle = fonts["body"].render("Pick a game and start playing.", True, (196, 207, 216))
    screen.blit(subtitle, (rect.x, rect.y + 42))

    control_y = rect.y + 82
    tabs = _draw_mode_tabs(
        pygame, screen, pygame.Rect(rect.x, control_y, min(384, rect.width), 44), fonts, selected_mode
    )
    detail_top = control_y + 58
    detail_height = 44 if games and rect.width > 520 else 0
    grid_top = control_y + 70 + detail_height
    search_target = None
    control_targets = {}
    if rect.width > 760:
        search = pygame.Rect(rect.right - 360, control_y, 212, 44)
        filter_btn = pygame.Rect(rect.right - 138, control_y, 66, 44)
        sort_btn = pygame.Rect(rect.right - 64, control_y, 64, 44)
        _draw_search_box(pygame, screen, search, fonts, search_query, search_active)
        _draw_pill(
            pygame, screen, filter_btn, "Filter", fonts["small_bold"], theme.PANEL, theme.TEXT, theme.BORDER_SUBTLE
        )
        _draw_pill(pygame, screen, sort_btn, "Sort", fonts["small_bold"], theme.PANEL, theme.TEXT, theme.BORDER_SUBTLE)
        search_target = search
        control_targets["filter"] = filter_btn
        control_targets["sort"] = sort_btn
    elif rect.width > 420:
        search = pygame.Rect(rect.x, control_y + 56, rect.width, 44)
        _draw_search_box(pygame, screen, search, fonts, search_query, search_active)
        grid_top += 56
        detail_top += 56
        search_target = search

    if games and detail_height:
        focused_game = games[max(0, min(focused_index, len(games) - 1))]
        _draw_game_detail_strip(
            pygame, screen, pygame.Rect(rect.x, detail_top, rect.width, detail_height), fonts, focused_game
        )
    elif search_query or selected_filter != MODE_ALL or selected_mode != MODE_ALL:
        reset_rect = pygame.Rect(rect.x, detail_top, min(220, rect.width), 34)
        _draw_pill(
            pygame,
            screen,
            reset_rect,
            "No matches - reset filters",
            fonts["small_bold"],
            theme.PANEL,
            theme.TEXT,
            theme.BORDER_SUBTLE,
        )

    grid = pygame.Rect(rect.x, grid_top, rect.width, rect.bottom - grid_top)
    columns = grid_columns(grid.width)
    gap = theme.SPACE_6
    card_w = min(CARD_MAX_WIDTH, (grid.width - gap * (columns - 1)) // columns)
    row_width = card_w * columns + gap * (columns - 1)
    start_x = grid.x + max(0, (grid.width - row_width) // 2)
    card_h = CARD_MIN_HEIGHT
    clickable = []
    for index, game in enumerate(games):
        row = index // columns
        col = index % columns
        card = pygame.Rect(start_x + col * (card_w + gap), grid.y + row * (card_h + gap), card_w, card_h)
        if card.bottom > rect.bottom:
            continue
        drawn = _draw_game_card(
            pygame,
            screen,
            card,
            fonts,
            game,
            hover_amount=hover_amounts.get(game.descriptor.game_id, 0.0),
            focused=index == focused_index,
            asset_service=asset_service,
        )
        clickable.append((drawn, game))
    if not games:
        empty = pygame.Rect(grid.x, grid.y + 20, grid.width, 150)
        _draw_panel(pygame, screen, empty, theme.PANEL, theme.BORDER_SUBTLE)
        draw_text(pygame, screen, fonts["body_bold"], "No games in this category yet", empty.center, theme.MUTED)
    result_text = f"{len(games)} game" + ("" if len(games) == 1 else "s")
    result_surface = fonts["small"].render(result_text, True, theme.SUBTLE)
    screen.blit(result_surface, (rect.x, max(rect.y + 64, control_y - 22)))
    if control_panel:
        panel_rect = pygame.Rect(rect.right - 280, control_y + 54, 260, 96)
        _draw_panel(pygame, screen, panel_rect, theme.SIDEBAR, theme.BORDER_SUBTLE, theme.RADIUS_MD)
        if control_panel == "filter":
            lines = ("Filters", "Use category + All / 1P / 2P", "More filters coming soon")
        else:
            lines = ("Sort", "Featured first", "Name sort coming soon")
        screen.blit(fonts["body_bold"].render(lines[0], True, theme.TEXT), (panel_rect.x + 14, panel_rect.y + 12))
        screen.blit(fonts["small"].render(lines[1], True, theme.MUTED), (panel_rect.x + 14, panel_rect.y + 42))
        screen.blit(fonts["small"].render(lines[2], True, theme.SUBTLE), (panel_rect.x + 14, panel_rect.y + 66))
    return clickable, tabs, search_target, control_targets


def _draw_right_panel(pygame, screen, rect, fonts, wallet):
    if rect is None:
        return
    _draw_panel(pygame, screen, rect, theme.SIDEBAR, theme.BORDER_SUBTLE)
    x = rect.x + 18
    y = rect.y + 18
    screen.blit(fonts["body_bold"].render("Wallet", True, theme.TEXT), (x, y))
    y += 38
    _draw_pill(
        pygame,
        screen,
        pygame.Rect(x, y, rect.width - 36, 38),
        wallet["network"],
        fonts["small_bold"],
        theme.BLUE,
        (255, 255, 255),
    )
    y += 54
    screen.blit(fonts["small"].render("Status", True, theme.MUTED), (x, y))
    screen.blit(fonts["body_bold"].render(wallet["status"].replace("-", " ").title(), True, theme.TEXT), (x, y + 20))
    y += 68
    screen.blit(fonts["small"].render("Balance", True, theme.MUTED), (x, y))
    screen.blit(fonts["body_bold"].render(wallet["balance"], True, theme.TEXT), (x, y + 20))
    screen.blit(fonts["small"].render("No fiat value without a trusted feed", True, theme.MUTED), (x, y + 48))
    y += 92
    screen.blit(fonts["body_bold"].render("Rewards Gallery", True, theme.TEXT), (x, y))
    screen.blit(fonts["small"].render("NFT souvenirs: Coming soon", True, theme.MUTED), (x, y + 30))
    gallery_y = y + 66
    for index in range(4):
        tile = pygame.Rect(x + (index % 2) * 126, gallery_y + (index // 2) * 92, 108, 74)
        pygame.draw.rect(screen, theme.PANEL, tile, border_radius=theme.RADIUS_MD)
        pygame.draw.rect(screen, theme.BORDER_SUBTLE, tile, 1, border_radius=theme.RADIUS_MD)
        draw_fallback_icon(pygame, screen, pygame.Rect(tile.x + 32, tile.y + 15, 44, 44), "NFT", theme.AMBER)
    y = rect.bottom - 142
    screen.blit(fonts["body_bold"].render("Player Stats", True, theme.TEXT), (x, y))
    for offset, line in enumerate(("Win rate  --", "Games played  --", "Tournament rank  --")):
        screen.blit(fonts["small"].render(line, True, theme.MUTED), (x, y + 34 + offset * 24))


def _draw_tournament_dock(pygame, screen, rect, fonts, eligible_count=0):
    pygame.draw.rect(screen, (35, 47, 58), rect)
    pygame.draw.line(screen, theme.BORDER, (0, rect.y), (rect.width, rect.y), 1)
    if rect.width < 560:
        cta = pygame.Rect(theme.SPACE_4, rect.y + 14, rect.width - theme.SPACE_8, rect.height - 28)
        pygame.draw.rect(screen, theme.ACCENT, cta, border_radius=theme.RADIUS_LG)
        pygame.draw.rect(screen, (39, 139, 59), cta, 2, border_radius=theme.RADIUS_LG)
        title = _fit_text(pygame, fonts["heading"], "Tournament", cta.width - 24, (255, 255, 255))
        screen.blit(title, title.get_rect(center=cta.center))
        return cta

    collapse = pygame.Rect(rect.right - 42, rect.y + 22, 28, 28)
    pygame.draw.rect(screen, theme.RAISED, collapse, border_radius=theme.RADIUS_SM)
    collapse_icon = fonts["small_bold"].render("-", True, theme.TEXT)
    screen.blit(collapse_icon, collapse_icon.get_rect(center=collapse.center))

    player_w = min(210, rect.width // 5)
    left = pygame.Rect(theme.SPACE_6, rect.y + 12, player_w, rect.height - 24)
    right = pygame.Rect(rect.right - player_w - 58, rect.y + 12, player_w, rect.height - 24)
    cta = pygame.Rect(
        left.right + theme.SPACE_5, rect.y + 13, right.left - left.right - theme.SPACE_10, rect.height - 26
    )
    pygame.draw.rect(screen, (68, 48, 55), left, border_radius=theme.RADIUS_LG)
    pygame.draw.rect(screen, (40, 68, 78), right, border_radius=theme.RADIUS_LG)
    pygame.draw.circle(screen, theme.PLAYER_ONE, (left.x + 28, left.centery), 18)
    pygame.draw.circle(screen, theme.PLAYER_TWO, (right.x + 28, right.centery), 18)
    screen.blit(fonts["small_bold"].render("Me", True, theme.TEXT), (left.x + 56, left.y + 12))
    screen.blit(fonts["body_bold"].render("Score 0", True, theme.TEXT), (left.x + 56, left.y + 34))
    screen.blit(fonts["small_bold"].render("Waiting for a rival", True, theme.TEXT), (right.x + 56, right.y + 12))
    screen.blit(fonts["body_bold"].render("Score 0", True, theme.TEXT), (right.x + 56, right.y + 34))
    pygame.draw.rect(screen, theme.ACCENT, cta, border_radius=theme.RADIUS_LG)
    pygame.draw.rect(screen, (39, 139, 59), cta, 2, border_radius=theme.RADIUS_LG)
    title = _fit_text(pygame, fonts["heading"], "Tournament", cta.width - 28, (255, 255, 255))
    screen.blit(title, title.get_rect(center=cta.center))
    return cta


def _draw_tournament_lobby(pygame, screen, fonts, games):
    width, height = screen.get_size()
    overlay = pygame.Rect(max(24, (width - 560) // 2), 110, min(560, width - 48), min(430, height - 180))
    _draw_panel(pygame, screen, overlay, theme.SIDEBAR, theme.BORDER, theme.RADIUS_XL)
    screen.blit(fonts["heading"].render("Tournament lobby", True, theme.TEXT), (overlay.x + 24, overlay.y + 22))
    count_text = f"{len(games)} two-player game" + ("" if len(games) == 1 else "s")
    screen.blit(fonts["body"].render(count_text, True, theme.MUTED), (overlay.x + 24, overlay.y + 64))
    y = overlay.y + 108
    if not games:
        screen.blit(fonts["body"].render("No tournament-ready games yet.", True, theme.MUTED), (overlay.x + 24, y))
    for index, game in enumerate(games):
        row = pygame.Rect(overlay.x + 24, y + index * 48, overlay.width - 48, 38)
        pygame.draw.rect(screen, theme.PANEL, row, border_radius=theme.RADIUS_MD)
        screen.blit(
            fonts["body_bold"].render(f"{index + 1}. {game.descriptor.title}", True, theme.TEXT),
            (row.x + 14, row.y + 8),
        )
    hint = fonts["small"].render("Local 2-player tournament. Press Esc to close.", True, theme.SUBTLE)
    screen.blit(hint, (overlay.x + 24, overlay.bottom - 38))


def run_library_scene(pygame, context, registry) -> SceneResult:
    """Show the desktop game hub and return the selected game id."""

    screen = context.screen
    clock = context.clock
    fonts = {
        "title": context.assets.font(pygame, "display", theme.TEXT_2XL, bold=True),
        "heading": context.assets.font(pygame, "display", theme.TEXT_XL, bold=True),
        "card_title": context.assets.font(pygame, "body", 24, bold=True),
        "body": context.assets.font(pygame, "body", theme.TEXT_MD),
        "body_bold": context.assets.font(pygame, "body", theme.TEXT_MD, bold=True),
        "small": context.assets.font(pygame, "body", 14),
        "small_bold": context.assets.font(pygame, "body", 14, bold=True),
        "tiny_bold": context.assets.font(pygame, "body", theme.TEXT_XS, bold=True),
    }
    selected_filter = MODE_ALL
    selected_mode = MODE_ALL
    search_query = ""
    search_active = False
    focused_card_index = 0
    hover_amounts: dict[str, float] = {}
    sidebar_targets = []
    card_targets = []
    tab_targets = []
    search_target = None
    control_targets = {}
    top_nav_targets = {}
    tournament_start_rect = None
    control_panel = None
    feedback = ""
    tournament_lobby_games = None

    while True:
        context.audio.update()
        mouse_pos = pygame.mouse.get_pos()
        games = registry.list_all()
        visible_games = filter_games(games, selected_filter, selected_mode, search_query)
        if visible_games:
            focused_card_index = max(0, min(focused_card_index, len(visible_games) - 1))
        else:
            focused_card_index = 0
        layout = compute_hub_layout(pygame, screen.get_size())
        wallet = wallet_summary(context)
        hovered_game_ids = {game.descriptor.game_id for rect, game in card_targets if rect.collidepoint(mouse_pos)}
        visible_game_ids = {game.descriptor.game_id for game in visible_games}
        for game_id in list(hover_amounts):
            if game_id not in visible_game_ids:
                del hover_amounts[game_id]
        for game in visible_games:
            game_id = game.descriptor.game_id
            current = hover_amounts.get(game_id, 0.0)
            target = 1.0 if game_id in hovered_game_ids else 0.0
            hover_amounts[game_id] = current + (target - current) * 0.24

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if tournament_lobby_games is not None:
                        tournament_lobby_games = None
                    elif control_panel:
                        control_panel = None
                    elif search_active or search_query:
                        search_active = False
                        search_query = ""
                        focused_card_index = 0
                    else:
                        return SceneResult(PlatformAction.HOME)
                elif event.key == pygame.K_SLASH:
                    search_active = True
                elif search_active and event.key == pygame.K_BACKSPACE:
                    search_query = search_query[:-1]
                    focused_card_index = 0
                elif search_active and event.key == pygame.K_RETURN:
                    search_active = False
                elif search_active and event.unicode and event.unicode.isprintable():
                    search_query = (search_query + event.unicode)[:32]
                    focused_card_index = 0
                if not search_active and event.key == pygame.K_1:
                    selected_mode = MODE_SINGLE
                    focused_card_index = 0
                if not search_active and event.key == pygame.K_2:
                    selected_mode = MODE_TWO
                    focused_card_index = 0
                if not search_active and event.key == pygame.K_a:
                    selected_mode = MODE_ALL
                    focused_card_index = 0
                if not search_active and event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_TAB) and visible_games:
                    focused_card_index = (focused_card_index + 1) % len(visible_games)
                if not search_active and event.key in (pygame.K_LEFT, pygame.K_UP) and visible_games:
                    focused_card_index = (focused_card_index - 1) % len(visible_games)
                if not search_active and event.key in (pygame.K_RETURN, pygame.K_SPACE) and visible_games:
                    game = visible_games[focused_card_index]
                    if game.descriptor.enabled:
                        return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if tournament_lobby_games is not None:
                    tournament_lobby_games = None
                    continue
                if top_nav_targets.get("settings") and top_nav_targets["settings"].collidepoint(event.pos):
                    return SceneResult(PlatformAction.SETTINGS)
                if top_nav_targets.get("home") and top_nav_targets["home"].collidepoint(event.pos):
                    return SceneResult(PlatformAction.HOME)
                if top_nav_targets.get("leaderboard") and top_nav_targets["leaderboard"].collidepoint(event.pos):
                    return SceneResult(PlatformAction.LEADERBOARD)
                if top_nav_targets.get("rewards") and top_nav_targets["rewards"].collidepoint(event.pos):
                    return SceneResult(PlatformAction.REWARDS)
                if top_nav_targets.get("wallet") and top_nav_targets["wallet"].collidepoint(event.pos):
                    feedback = "No compatible wallet found"
                if search_target and search_target.collidepoint(event.pos):
                    search_active = True
                else:
                    search_active = False
                if control_targets.get("filter") and control_targets["filter"].collidepoint(event.pos):
                    control_panel = None if control_panel == "filter" else "filter"
                    feedback = "Filters ready"
                elif control_targets.get("sort") and control_targets["sort"].collidepoint(event.pos):
                    control_panel = None if control_panel == "sort" else "sort"
                    feedback = "Featured first"
                if tournament_start_rect and tournament_start_rect.collidepoint(event.pos):
                    tournament_lobby_games = select_tournament_games(games)
                    feedback = f"Tournament ready: {len(tournament_lobby_games)} games"
                for rect, key in sidebar_targets + tab_targets:
                    if rect.collidepoint(event.pos):
                        if key in (MODE_ALL, MODE_SINGLE, MODE_TWO):
                            selected_mode = key
                        else:
                            selected_filter = key
                        focused_card_index = 0
                if not visible_games and (search_query or selected_filter != MODE_ALL or selected_mode != MODE_ALL):
                    reset_rect = pygame.Rect(layout.main.x, layout.main.y + 140, min(220, layout.main.width), 34)
                    if reset_rect.collidepoint(event.pos):
                        selected_filter = MODE_ALL
                        selected_mode = MODE_ALL
                        search_query = ""
                        search_active = False
                for rect, game in card_targets:
                    if rect.collidepoint(event.pos) and game.descriptor.enabled:
                        return SceneResult(PlatformAction.LAUNCH_GAME, game_id=game.descriptor.game_id)

        screen.fill(theme.BG)
        _draw_top_nav(pygame, screen, layout.top_nav, fonts, wallet)
        next_top_nav_targets = _top_nav_targets(pygame, screen.get_width(), wallet, fonts["body_bold"])
        next_sidebar_targets = _draw_sidebar(
            pygame, screen, layout.sidebar, fonts, selected_filter, daily_challenge_title(games)
        )
        next_card_targets, next_tab_targets, next_search_target, next_control_targets = _draw_game_browser(
            pygame,
            screen,
            layout.main,
            fonts,
            visible_games,
            selected_filter,
            selected_mode,
            search_query,
            search_active,
            mouse_pos,
            focused_card_index,
            hover_amounts,
            control_panel,
            context.assets,
        )
        _draw_right_panel(pygame, screen, layout.right_panel, fonts, wallet)
        next_tournament_start_rect = _draw_tournament_dock(
            pygame, screen, layout.tournament, fonts, len(eligible_tournament_games(games))
        )
        if tournament_lobby_games is not None:
            _draw_tournament_lobby(pygame, screen, fonts, tournament_lobby_games)
        if feedback:
            toast = pygame.Rect(screen.get_width() // 2 - 150, TOP_NAV_HEIGHT + 10, 300, 40)
            _draw_panel(pygame, screen, toast, theme.PANEL, theme.BORDER_SUBTLE, theme.RADIUS_MD)
            draw_text(pygame, screen, fonts["small_bold"], feedback, toast.center, theme.TEXT)
        sidebar_targets = next_sidebar_targets
        card_targets = next_card_targets
        tab_targets = next_tab_targets
        search_target = next_search_target
        control_targets = next_control_targets
        top_nav_targets = next_top_nav_targets
        tournament_start_rect = next_tournament_start_rect

        pygame.display.flip()
        clock.tick(60)
