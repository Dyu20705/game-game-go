"""Color Wars public manifest."""

from pathlib import Path

from src.platform.games import GameDescriptor


DESCRIPTOR = GameDescriptor(
    game_id="color_wars",
    title="Color Wars",
    short_description="Turn-based chain-reaction strategy on a 5x5 board.",
    version="0.1.0",
    supported_modes=("pvp", "pvbot"),
    thumbnail=Path("games/color_wars/thumbnails/card.png"),
    enabled=True,
    sort_order=10,
    tags=("strategy", "turn-based", "ai"),
    author="Game Game Go",
    min_players=1,
    max_players=2,
)



