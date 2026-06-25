from src.platform.app import build_default_registry


def test_default_registry_contains_registered_games():
    registry = build_default_registry()

    assert registry.get("color_wars").descriptor.title == "Color Wars"
    assert registry.get("square_xo").descriptor.title == "SquareXO"
    assert registry.get("nuts_and_bolts").descriptor.title == "Nuts & Bolts"
    assert registry.get("demo_game").descriptor.title == "Click Sprint"
