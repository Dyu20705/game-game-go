"""Platform settings with safe defaults and persistence helpers."""

from dataclasses import asdict, dataclass


def clamp01(value: float) -> float:
    """Clamp a float to [0.0, 1.0]."""
    return max(0.0, min(1.0, float(value)))


@dataclass
class PlatformSettings:
    """Long-lived settings owned by the Game Game Go platform."""

    fullscreen: bool = False
    sound_enabled: bool = True
    master_volume: float = 0.8
    language: str = "vi"
    window_size: tuple[int, int] = (1100, 720)

    def set_master_volume(self, volume: float):
        self.master_volume = clamp01(volume)

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["window_size"] = list(self.window_size)
        return data

    @classmethod
    def from_dict(cls, data: object):
        if not isinstance(data, dict):
            return cls()
        width, height = (1100, 720)
        raw_size = data.get("window_size", [width, height])
        if isinstance(raw_size, list | tuple) and len(raw_size) == 2:
            try:
                width, height = int(raw_size[0]), int(raw_size[1])
            except (TypeError, ValueError):
                width, height = cls.window_size
        settings = cls(
            fullscreen=bool(data.get("fullscreen", False)),
            sound_enabled=bool(data.get("sound_enabled", True)),
            master_volume=clamp01(data.get("master_volume", 0.8)),
            language=str(data.get("language", "vi") or "vi"),
            window_size=(max(640, width), max(480, height)),
        )
        return settings


class SettingsService:
    """Manage platform settings and game-specific preference dictionaries."""

    def __init__(self, settings: PlatformSettings | None = None, games: dict[str, dict[str, object]] | None = None):
        self.platform = settings or PlatformSettings()
        self.games = games or {}

    def get_game_settings(self, game_id: str) -> dict[str, object]:
        return dict(self.games.get(game_id, {}))

    def update_game_settings(self, game_id: str, values: dict[str, object]):
        existing = dict(self.games.get(game_id, {}))
        existing.update(values)
        self.games[game_id] = existing

    def to_document(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "platform": self.platform.to_dict(),
            "games": self.games,
        }

    @classmethod
    def from_document(cls, document: object):
        if not isinstance(document, dict):
            return cls()
        settings = PlatformSettings.from_dict(document.get("platform", {}))
        games = document.get("games", {})
        if not isinstance(games, dict):
            games = {}
        clean_games = {
            str(game_id): dict(values)
            for game_id, values in games.items()
            if isinstance(values, dict)
        }
        return cls(settings=settings, games=clean_games)
