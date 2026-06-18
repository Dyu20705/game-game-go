"""Shared application-level settings passed across scenes and runtime loops."""

from dataclasses import dataclass


def clamp01(value: float) -> float:
    """Clamp float value to [0.0, 1.0]."""
    return max(0.0, min(1.0, float(value)))


@dataclass
class AppSettings:
    """Global user preferences shared by home/game scenes."""

    sound_enabled: bool = True
    sound_volume: float = 0.75
    fullscreen: bool = False
    language: str = "vi"

    def set_sound_enabled(self, enabled: bool):
        self.sound_enabled = bool(enabled)

    def set_sound_volume(self, volume: float):
        self.sound_volume = clamp01(volume)

    def set_fullscreen(self, fullscreen: bool):
        self.fullscreen = bool(fullscreen)

