from src.platform.services import PlatformSettings, SettingsService, clamp01


def test_platform_settings_defaults():
    service = SettingsService.from_document({})

    assert service.platform.sound_enabled is True
    assert service.platform.language == "vi"
    assert service.platform.master_volume == 0.8


def test_volume_is_clamped():
    settings = PlatformSettings()

    settings.set_master_volume(2.4)
    assert settings.master_volume == 1.0

    settings.set_master_volume(-5)
    assert settings.master_volume == 0.0
    assert clamp01(0.4) == 0.4


def test_game_settings_are_namespaced():
    service = SettingsService()

    service.update_game_settings("color_wars", {"last_mode": "pvp"})

    assert service.get_game_settings("color_wars") == {"last_mode": "pvp"}
    assert service.get_game_settings("demo_game") == {}

