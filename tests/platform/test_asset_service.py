from pathlib import Path

from src.platform.services import AssetService


def test_asset_service_resolves_legacy_color_wars_assets(tmp_path):
    service = AssetService(tmp_path)

    assert service.game("color_wars", "img/game_icon.png") == tmp_path / "asset" / "img" / "game_icon.png"


def test_asset_service_resolves_platform_namespace(tmp_path):
    service = AssetService(Path(tmp_path))

    assert service.platform("images/logo.png") == tmp_path / "asset" / "platform" / "images/logo.png"

