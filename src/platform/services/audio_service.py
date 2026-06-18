"""Shared audio service for menu music and mini-games."""

from pathlib import Path


class AudioService:
    """Small pygame mixer wrapper that tolerates missing audio support."""

    def __init__(self, settings, music_paths: list[Path] | None = None):
        self.settings = settings
        self.music_paths = list(music_paths or [])
        self._active_track: Path | None = None
        self._ready = False
        self._pygame = None

    def _ensure_ready(self) -> bool:
        if self._ready:
            return self._pygame is not None
        self._ready = True
        try:
            import pygame

            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self._pygame = pygame
        except Exception:
            self._pygame = None
        return self._pygame is not None

    def set_music_paths(self, paths: list[Path]):
        self.music_paths = list(paths)

    def play_menu_music(self):
        if not self.music_paths:
            return
        self.play_music(self.music_paths[0], loop=True)

    def play_music(self, path: Path, loop: bool = True):
        if not self._ensure_ready():
            return
        if self._active_track == path and self._pygame.mixer.music.get_busy():
            self.apply_preferences()
            return
        try:
            self._pygame.mixer.music.load(str(path))
            self._pygame.mixer.music.set_volume(self.settings.platform.master_volume)
            self._pygame.mixer.music.play(-1 if loop else 0)
            self._active_track = path
            self.apply_preferences()
        except Exception:
            self._active_track = None

    def apply_preferences(self):
        if not self._ensure_ready():
            return
        try:
            self._pygame.mixer.music.set_volume(self.settings.platform.master_volume)
            if self.settings.platform.sound_enabled:
                self._pygame.mixer.music.unpause()
            else:
                self._pygame.mixer.music.pause()
        except Exception:
            return
