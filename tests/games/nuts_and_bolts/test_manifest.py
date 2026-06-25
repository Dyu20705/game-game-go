from src.games.nuts_and_bolts.manifest import DESCRIPTOR


def test_descriptor_metadata():
    assert DESCRIPTOR.game_id == "nuts_and_bolts"
    assert DESCRIPTOR.title == "Nuts & Bolts"
    assert DESCRIPTOR.supported_modes == ("solo",)
    assert DESCRIPTOR.enabled is True
    assert "puzzle" in DESCRIPTOR.tags
    assert DESCRIPTOR.min_players == 1
    assert DESCRIPTOR.max_players == 1
