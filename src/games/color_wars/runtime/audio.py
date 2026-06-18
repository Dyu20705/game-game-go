"""Background music controller with session-aware menu/game playlists."""

from pathlib import Path
import random

import pygame


def _resolve_music_paths():
    """Return all mp3 files sorted by name under asset/aud."""
    asset_dir = Path(__file__).resolve().parent.parent.parent / "asset" / "aud"
    if not asset_dir.exists():
        return []
    return sorted(asset_dir.glob("*.mp3"))


class MusicManager:
    """Manage one background track that loops across all scenes."""

    def __init__(self):
        self._mixer_ready = False
        self._tracks = []
        self._theme_track = None
        self._active_track = None
        self._enabled = True
        self._volume = 0.75

    @staticmethod
    def _clamp01(value):
        return max(0.0, min(1.0, float(value)))

    def _ensure_ready(self):
        if self._mixer_ready:
            return bool(self._tracks)

        self._tracks = _resolve_music_paths()
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init()
            self._mixer_ready = True
        except pygame.error:
            self._mixer_ready = True
            self._tracks = []
            return False
        return bool(self._tracks)

    def start_new_menu_session(self):
        """Pick one track for the whole runtime session."""
        if not self._ensure_ready():
            return

        if self._theme_track is not None:
            return

        shuffled = self._tracks[:]
        random.shuffle(shuffled)
        self._theme_track = shuffled[0]

    def _load_and_play(self, track):
        if track is None or not self._ensure_ready():
            return
        if self._active_track == track:
            return
        try:
            pygame.mixer.music.load(str(track))
            pygame.mixer.music.set_volume(self._volume)
            pygame.mixer.music.play(-1)
            if not self._enabled:
                pygame.mixer.music.pause()
            self._active_track = track
        except (pygame.error, FileNotFoundError, OSError):
            pass

    def enter_menu(self):
        """Ensure the shared looping track is loaded and playing."""
        if self._theme_track is None:
            self.start_new_menu_session()
        self._load_and_play(self._theme_track)
        self.apply_audio_preferences(self._enabled, self._volume)

    def enter_gameplay(self):
        """Keep the same looping track playing (no reload)."""
        if self._theme_track is None:
            self.start_new_menu_session()
        if self._active_track == self._theme_track and pygame.mixer.music.get_busy():
            return
        self._load_and_play(self._theme_track)
        self.apply_audio_preferences(self._enabled, self._volume)

    def apply_audio_preferences(self, enabled, volume):
        """Apply volume and pause/resume state without forced restart."""
        self._enabled = bool(enabled)
        self._volume = self._clamp01(volume)
        if not self._ensure_ready():
            return
        try:
            pygame.mixer.music.set_volume(self._volume)
            if self._enabled:
                pygame.mixer.music.unpause()
                if self._active_track is not None and not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.pause()
        except pygame.error:
            pass


_GLOBAL_MUSIC_MANAGER = MusicManager()


def get_music_manager():
    """Return shared music manager instance."""
    return _GLOBAL_MUSIC_MANAGER


def set_music_enabled(enabled, volume=0.75):
    """Backwards-compatible wrapper used by existing callers."""
    _GLOBAL_MUSIC_MANAGER.apply_audio_preferences(enabled, volume)


def update_music_volume(volume):
    """Backwards-compatible wrapper to update volume only."""
    _GLOBAL_MUSIC_MANAGER.apply_audio_preferences(_GLOBAL_MUSIC_MANAGER._enabled, volume)

