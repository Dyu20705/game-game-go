import pytest

from src.platform.games import GameDescriptor


def test_descriptor_requires_game_id():
    with pytest.raises(ValueError):
        GameDescriptor(
            game_id="",
            title="Broken",
            short_description="bad",
            version="0",
            supported_modes=("solo",),
        )


def test_descriptor_accepts_optional_metadata():
    descriptor = GameDescriptor(
        game_id="sample",
        title="Sample",
        short_description="A sample game",
        version="1.0",
        supported_modes=("solo",),
        tags=("demo",),
        min_players=1,
        max_players=2,
    )

    assert descriptor.game_id == "sample"
    assert descriptor.tags == ("demo",)

