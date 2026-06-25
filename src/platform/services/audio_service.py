"""Shared audio service for menu music and mini-games."""

import random
from pathlib import Path


class AudioService:
    """Small pygame mixer wrapper that tolerates missing audio support."""

    def __init__(self, settings, music_paths: list[Path] | None = None):
        self.settings = settings
        self.music_paths = list(music_paths or [])
        self._active_track: Path | None = None
        self._shuffle_bag: list[Path] = []
        self._last_track: Path | None = None
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
        self._shuffle_bag = []

    @property
    def current_track_title(self) -> str:
        if self._active_track is None:
            return "No track"
        return _format_track_title(self._active_track)

    @property
    def is_playing(self) -> bool:
        if not self._ensure_ready():
            return False
        try:
            return bool(self._pygame.mixer.music.get_busy()) and self.settings.platform.sound_enabled
        except Exception:
            return False

    def play_menu_music(self):
        if not self.music_paths:
            return
        self.play_music(self.next_track_path(), loop=False)

    def next_track_path(self) -> Path:
        if not self.music_paths:
            raise ValueError("No music tracks are configured")
        if not self._shuffle_bag:
            self._shuffle_bag = list(self.music_paths)
            random.shuffle(self._shuffle_bag)
            if len(self._shuffle_bag) > 1 and self._last_track == self._shuffle_bag[0]:
                self._shuffle_bag.append(self._shuffle_bag.pop(0))
        track = self._shuffle_bag.pop(0)
        self._last_track = track
        return track

    def next_track(self):
        if not self.music_paths:
            return
        self.play_music(self.next_track_path(), loop=False)

    def update(self):
        if not self.music_paths or not self.settings.platform.sound_enabled:
            return
        if not self._ensure_ready():
            return
        try:
            if self._active_track is not None and not self._pygame.mixer.music.get_busy():
                self.next_track()
        except Exception:
            return

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

    def pause(self):
        if not self._ensure_ready():
            return
        try:
            self._pygame.mixer.music.pause()
        except Exception:
            return

    def resume(self):
        if not self._ensure_ready():
            return
        try:
            self._pygame.mixer.music.unpause()
        except Exception:
            return

    def toggle_music(self):
        self.settings.platform.sound_enabled = not self.settings.platform.sound_enabled
        self.apply_preferences()


def _format_track_title(path: Path) -> str:
    title = path.stem
    title = title.replace("(Extended Mix)", "").replace("(320 Kbps)", "")
    title = " ".join(title.replace("_", " ").replace("-", " - ").split())
    return title.strip(" -") or "Unknown track"
