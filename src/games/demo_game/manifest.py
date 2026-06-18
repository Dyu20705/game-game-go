"""Demo game manifest."""

from src.platform.games import GameDescriptor


DESCRIPTOR = GameDescriptor(
    game_id="demo_game",
    title="Click Sprint",
    short_description="Click the moving target before the short timer ends.",
    version="0.1.0",
    supported_modes=("solo",),
    enabled=True,
    sort_order=20,
    tags=("arcade", "demo"),
    author="Game Game Go",
    min_players=1,
    max_players=1,
)

