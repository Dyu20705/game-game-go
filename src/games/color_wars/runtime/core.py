"""Core runtime systems for scene flow, settings, and audio orchestration."""

from dataclasses import dataclass
from enum import Enum

from src.games.color_wars.runtime.audio import get_music_manager
from src.games.color_wars.runtime.settings import AppSettings


class SceneName(str, Enum):
    """High-level application scenes used by the runtime state machine."""

    HOME = "home"
    GAMEPLAY = "gameplay"
    QUIT = "quit"


@dataclass
class LaunchConfig:
    """Validated launch parameters used to start a match."""

    game_mode: str = "pvbot"
    difficulty: str = "easy"


class CoreSystems:
    """Single source of truth for app-level systems and transitions."""

    def __init__(self):
        self.settings = AppSettings()
        self.music = get_music_manager()
        self.current_scene = SceneName.HOME
        self.active_launch = LaunchConfig()

    def begin_home_session(self):
        """Start a new menu session and randomize theme/game tracks."""
        self.music.start_new_menu_session()
        self.music.enter_menu()

    def enter_gameplay(self, launch: LaunchConfig):
        """Transition to gameplay and apply latest audio preferences."""
        self.active_launch = launch
        self.current_scene = SceneName.GAMEPLAY
        self.music.enter_gameplay()
        self.music.apply_audio_preferences(self.settings.sound_enabled, self.settings.sound_volume)

    def enter_home(self):
        """Transition back to home and restore theme music context."""
        self.current_scene = SceneName.HOME
        self.music.enter_menu()

    def request_quit(self):
        """Mark runtime for shutdown."""
        self.current_scene = SceneName.QUIT


