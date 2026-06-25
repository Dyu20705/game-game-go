from datetime import date
from types import SimpleNamespace

from src.platform.blockchain.domain.network import ChainHealth, ChainHealthStatus
from src.platform.games import GameCapability, GameDescriptor
from src.platform.scenes.library_scene import (
    MODE_SINGLE,
    MODE_TWO,
    TOURNAMENT_DOCK_HEIGHT,
    compute_hub_layout,
    daily_challenge_title,
    eligible_tournament_games,
    entry_fee_label,
    filter_games,
    game_mode,
    grid_columns,
    select_tournament_games,
    settlement_mode,
    wallet_requirement_label,
    wallet_summary,
)


def _game(descriptor):
    return SimpleNamespace(descriptor=descriptor)


def test_grid_columns_scale_for_desktop_and_mobile():
    assert grid_columns(1300) == 4
    assert grid_columns(1100) == 3
    assert grid_columns(900) == 2
    assert grid_columns(640) == 2
    assert grid_columns(420) == 1


def test_layout_keeps_right_panel_for_wide_desktop_only():
    import pygame

    laptop = compute_hub_layout(pygame, (1440, 900))
    desktop = compute_hub_layout(pygame, (1920, 1080))

    assert laptop.right_panel is None
    assert laptop.main.width >= 980
    assert desktop.right_panel is not None
    assert desktop.main.right < desktop.right_panel.left


def test_layout_reserves_space_for_tournament_dock():
    import pygame

    layout = compute_hub_layout(pygame, (1366, 768))

    assert layout.tournament.height == TOURNAMENT_DOCK_HEIGHT
    assert layout.main.bottom < layout.tournament.top


def test_game_mode_uses_player_range():
    solo = GameDescriptor("solo", "Solo", "One player", "1", ("solo",), min_players=1, max_players=1)
    duel = GameDescriptor("duel", "Duel", "Two players", "1", ("local_1v1",), min_players=2, max_players=2)

    assert game_mode(solo) == MODE_SINGLE
    assert game_mode(duel) == MODE_TWO


def test_filter_games_by_mode_and_on_chain_capability():
    solo = _game(GameDescriptor("solo", "Solo", "One player", "1", ("solo",), min_players=1, max_players=1))
    duel = _game(
        GameDescriptor(
            "duel",
            "Duel",
            "Two players",
            "1",
            ("local_1v1",),
            min_players=2,
            max_players=2,
            capabilities=(GameCapability.VERIFIED_RESULT,),
        )
    )

    assert filter_games([solo, duel], "all", MODE_SINGLE) == [solo]
    assert filter_games([solo, duel], "all", MODE_TWO) == [duel]
    assert filter_games([solo, duel], "on-chain") == [duel]
    assert settlement_mode(duel.descriptor) == "hybrid"


def test_filter_games_combines_category_mode_and_search():
    arcade = _game(GameDescriptor("sprint", "Click Sprint", "Fast arcade clicks", "1", ("solo",), tags=("arcade",)))
    strategy = _game(
        GameDescriptor(
            "square",
            "SquareXO",
            "Claim squares",
            "1",
            ("local_1v1",),
            tags=("strategy",),
            min_players=2,
            max_players=2,
        )
    )

    assert filter_games([arcade, strategy], "strategy", MODE_TWO, "square") == [strategy]
    assert filter_games([arcade, strategy], "strategy", MODE_SINGLE, "square") == []


def test_card_labels_do_not_invent_fee_or_wallet_requirement():
    solo = GameDescriptor("solo", "Solo", "One player", "1", ("solo",), min_players=1, max_players=1)
    chain_ready = GameDescriptor(
        "chain",
        "Chain",
        "Chain capable",
        "1",
        ("local_1v1",),
        min_players=2,
        max_players=2,
        capabilities=(GameCapability.VERIFIED_RESULT,),
    )

    assert entry_fee_label(solo) == "Free"
    assert wallet_requirement_label(solo) == "Wallet not required to play"
    assert wallet_requirement_label(chain_ready) == "Wallet only required before on-chain actions"


def test_tournament_uses_real_two_player_games_only():
    solo = _game(GameDescriptor("solo", "Solo", "One player", "1", ("solo",), min_players=1, max_players=1))
    duel = _game(GameDescriptor("duel", "Duel", "Two players", "1", ("local_1v1",), min_players=2, max_players=2))

    assert eligible_tournament_games([solo, duel]) == [duel]
    assert select_tournament_games([solo, duel], limit=7) == [duel]


def test_daily_challenge_uses_enabled_registered_game():
    games = [
        _game(GameDescriptor("one", "One", "First", "1", ("solo",), enabled=True)),
        _game(GameDescriptor("two", "Two", "Second", "1", ("solo",), enabled=True)),
    ]

    title = daily_challenge_title(games, today=date(2026, 6, 18))

    assert title in {"One", "Two"}


def test_wallet_summary_reports_offline_without_fake_balance():
    context = SimpleNamespace(blockchain=None)

    summary = wallet_summary(context)

    assert summary["status"] == "disconnected"
    assert summary["balance"] == "---- ROSE"


def test_wallet_summary_reports_local_identity():
    blockchain = SimpleNamespace(
        config=SimpleNamespace(mode=SimpleNamespace(value="local")),
        health=lambda: ChainHealth(ChainHealthStatus.CONNECTED, ChainHealthStatus.CONNECTED, "local"),
    )
    context = SimpleNamespace(blockchain=blockchain)

    summary = wallet_summary(context)

    assert summary["status"] == "connected"
    assert summary["detail"] == "Local dev identity"
