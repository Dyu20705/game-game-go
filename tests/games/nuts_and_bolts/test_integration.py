from src.platform.app import build_default_registry


def test_default_registry_contains_nuts_and_bolts():
    game = build_default_registry().get("nuts_and_bolts")

    assert game.descriptor.title == "Nuts & Bolts"
    assert game.descriptor.game_id == "nuts_and_bolts"
