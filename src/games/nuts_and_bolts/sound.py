from __future__ import annotations

from typing import Any


class SoundManager:
    """Game-local SFX adapter controlled by platform audio preferences."""

    def __init__(self, context: Any) -> None:
        self.context = context

    @property
    def enabled(self) -> bool:
        return bool(getattr(self.context.settings.platform, "sound_enabled", True))

    @property
    def volume(self) -> float:
        volume = getattr(self.context.settings.platform, "master_volume", 0.8)
        try:
            return max(0.0, min(1.0, float(volume)))
        except (TypeError, ValueError):
            return 0.8

    def play(self, _name: str) -> None:
        if not self.enabled or self.volume <= 0:
            return
        # No Nuts & Bolts SFX assets are bundled yet.

    def toggle(self) -> None:
        audio = getattr(self.context, "audio", None)
        if audio is not None and hasattr(audio, "toggle_music"):
            audio.toggle_music()
            return
        self.context.settings.platform.sound_enabled = not self.enabled
