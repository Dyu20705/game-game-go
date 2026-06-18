"""Path resolver for platform, game, and legacy assets."""

from pathlib import Path


class AssetService:
    """Resolve assets without depending on the current working directory."""

    def __init__(self, repository_root: Path):
        self.repository_root = Path(repository_root)

    def platform(self, relative_path: str) -> Path:
        return self.repository_root / "asset" / "platform" / relative_path

    def game(self, game_id: str, relative_path: str) -> Path:
        game_asset = self.repository_root / "src" / "games" / game_id / "assets" / relative_path
        if game_asset.exists():
            return game_asset
        if game_id == "color_wars":
            return self.legacy(relative_path)
        return game_asset

    def legacy(self, relative_path: str) -> Path:
        return self.repository_root / "asset" / relative_path

    def fallback_image(self) -> Path:
        return self.repository_root / "asset" / "img" / "game_icon.png"

