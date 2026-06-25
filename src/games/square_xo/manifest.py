"""SquareXO manifest."""

from pathlib import Path

from src.platform.games import GameCapability, GameDescriptor

DESCRIPTOR = GameDescriptor(
    game_id="square_xo",
    title="SquareXO",
    short_description="Claim edges, complete squares, and outscore your opponent.",
    version="0.1.0",
    supported_modes=("local_1v1",),
    thumbnail=Path("games/square_xo/thumbnails/card.png"),
    enabled=True,
    sort_order=15,
    tags=("strategy", "1v1", "dots-and-boxes"),
    capabilities=(
        GameCapability.LOCAL_PLAY,
        GameCapability.ONLINE_MULTIPLAYER,
        GameCapability.CONFIDENTIAL_MATCH,
        GameCapability.VERIFIED_RESULT,
    ),
    author="SquareXO authors / Game Game Go port",
    min_players=2,
    max_players=2,
)
