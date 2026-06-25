import os
from types import SimpleNamespace

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

from src.games.nuts_and_bolts.game import NutsAndBoltsGame
from src.games.nuts_and_bolts.manifest import DESCRIPTOR
from src.games.nuts_and_bolts.rules import can_move, capture_state, move_nut
from src.games.nuts_and_bolts.session import NutsAndBoltsSession
from src.platform.context import PlatformContext
from src.platform.games import GameExitAction, GameLaunchOptions
from src.platform.services.settings_service import SettingsService


class FakeAudio:
    def __init__(self, settings):
        self.settings = settings

    def toggle_music(self):
        self.settings.platform.sound_enabled = not self.settings.platform.sound_enabled


@pytest.fixture
def context():
    pygame.init()
    screen = pygame.display.set_mode((900, 620))
    settings = SettingsService()
    ctx = PlatformContext(
        screen=screen,
        clock=pygame.time.Clock(),
        settings=settings,
        audio=FakeAudio(settings),
        assets=SimpleNamespace(),
        save=SimpleNamespace(),
        localization=SimpleNamespace(),
    )
    yield ctx
    pygame.quit()


def make_session(context, launch_options=None):
    return NutsAndBoltsSession(context, launch_options or GameLaunchOptions())


def test_adapter_creates_session(context):
    game = NutsAndBoltsGame()

    assert game.descriptor is DESCRIPTOR
    session = game.create_session(context, GameLaunchOptions(difficulty="easy"))
    assert isinstance(session, NutsAndBoltsSession)
    assert session.context is context
    assert session.launch_options.difficulty == "easy"


def test_launch_difficulty_is_applied(context):
    session = make_session(context, GameLaunchOptions(difficulty="hard"))

    assert session.difficulty_key == "hard"


def test_invalid_launch_difficulty_reads_preference(context):
    context.settings.update_game_settings("nuts_and_bolts", {"last_difficulty": "easy"})

    session = make_session(context, GameLaunchOptions(difficulty="impossible"))

    assert session.difficulty_key == "easy"


def test_invalid_difficulty_falls_back_to_normal(context):
    context.settings.update_game_settings("nuts_and_bolts", {"last_difficulty": "expert"})

    session = make_session(context, GameLaunchOptions(difficulty="impossible"))

    assert session.difficulty_key == "normal"


def test_escape_returns_game_library(context):
    session = make_session(context)

    result = session.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

    assert result is not None
    assert result.action == GameExitAction.GAME_LIBRARY
    assert result.payload["difficulty"] == session.difficulty_key


def test_quit_event_returns_quit(context):
    session = make_session(context)

    result = session.handle_event(pygame.event.Event(pygame.QUIT))

    assert result is not None
    assert result.action == GameExitAction.QUIT


def test_apply_difficulty_persists_last_difficulty(context):
    session = make_session(context)

    session.apply_difficulty("hard")

    settings = context.settings.get_game_settings("nuts_and_bolts")
    assert settings["last_difficulty"] == "hard"


def test_completion_stats_are_recorded_once_and_best_moves_keeps_lowest(context):
    session = make_session(context)
    session.difficulty_key = "easy"
    session.move_count = 12

    session.record_completion()
    session.record_completion()

    settings = context.settings.get_game_settings("nuts_and_bolts")
    assert settings["total_completed"] == 1
    assert settings["best_moves_easy"] == 12

    session.completion_recorded = False
    session.move_count = 20
    session.record_completion()

    settings = context.settings.get_game_settings("nuts_and_bolts")
    assert settings["total_completed"] == 2
    assert settings["best_moves_easy"] == 12

    session.completion_recorded = False
    session.move_count = 8
    session.record_completion()

    settings = context.settings.get_game_settings("nuts_and_bolts")
    assert settings["total_completed"] == 3
    assert settings["best_moves_easy"] == 8


def test_undo_restores_previous_logical_state(context):
    session = make_session(context)
    before = capture_state(session.screws)
    source, destination = next(
        (s, d) for s in range(len(session.screws)) for d in range(len(session.screws)) if can_move(session.screws, s, d)
    )

    session.start_move(source, destination)
    session.finish_animation()
    assert session.move_count == 1

    session.undo()
    session.finish_animation()

    assert capture_state(session.screws) == before
    assert session.move_count == 0
    assert session.history == []


def test_restart_restores_initial_generated_state(context):
    session = make_session(context)
    initial = session.initial_state
    source, destination = next(
        (s, d)
        for s in range(len(session.screws))
        for d in range(len(session.screws))
        if s != d and session.screws[s].nuts and not session.screws[d].is_full()
    )
    move_nut(session.screws, source, destination)
    session.history.append((source, destination))
    session.move_count = 1

    session.restart()

    assert capture_state(session.screws) == initial
    assert session.history == []
    assert session.move_count == 0


def test_scramble_does_not_touch_move_count_or_history(context):
    session = make_session(context)

    assert session.move_count == 0
    assert session.history == []
