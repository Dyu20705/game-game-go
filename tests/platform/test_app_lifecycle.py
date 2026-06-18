from src.platform.app import build_default_registry


def test_default_registry_contains_color_wars_and_demo_game():
    registry = build_default_registry()

    assert registry.get("color_wars").descriptor.title == "Color Wars"
    assert registry.get("demo_game").descriptor.title == "Click Sprint"

