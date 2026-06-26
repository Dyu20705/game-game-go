"""Platform-level filesystem configuration."""

from dataclasses import dataclass
from pathlib import Path

from src.platform.version import APP_NAME


@dataclass(frozen=True)
class PlatformConfig:
    """Locations used by platform services."""

    app_name: str = APP_NAME
    repository_root: Path = Path(__file__).resolve().parents[2]
    save_path: Path = Path.home() / ".game_game_go" / "settings.json"
