from pathlib import Path
from types import SimpleNamespace

from src.platform.services.audio_service import AudioService


def _settings():
    return SimpleNamespace(platform=SimpleNamespace(sound_enabled=True, master_volume=0.8))


def test_audio_shuffle_bag_avoids_immediate_repeat_when_possible():
    tracks = [Path("one.mp3"), Path("two.mp3"), Path("three.mp3")]
    service = AudioService(_settings(), tracks)
    first_round = [service.next_track_path() for _ in tracks]
    next_track = service.next_track_path()

    assert sorted(first_round) == sorted(tracks)
    assert next_track != first_round[-1]


def test_audio_track_title_is_cleaned_from_filename():
    service = AudioService(_settings(), [Path("Sound Souler - Paradise (Extended Mix) - (320 Kbps).mp3")])
    service._active_track = service.music_paths[0]

    assert service.current_track_title == "Sound Souler - Paradise"


def test_audio_toggle_updates_persisted_setting():
    settings = _settings()
    service = AudioService(settings, [])

    service.toggle_music()

    assert settings.platform.sound_enabled is False
