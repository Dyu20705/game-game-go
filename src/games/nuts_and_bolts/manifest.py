"""Nuts & Bolts manifest."""

from src.platform.games import GameDescriptor


DESCRIPTOR = GameDescriptor(
    game_id="nuts_and_bolts",
    title="Nuts & Bolts",
    short_description="Move top nuts between screws until every colored screw is complete.",
    version="0.1.0",
    supported_modes=("solo",),
    enabled=True,
    sort_order=18,
    tags=("puzzle", "casual", "single-player"),
    author="Game Game Go",
    min_players=1,
    max_players=1,
)
