from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.scenes.scene_manager import SceneManager


def test_scene_manager_tracks_current_scene():
    manager = SceneManager()

    manager.go_to("library")

    assert manager.current == "library"


def test_scene_result_can_carry_game_id():
    result = SceneResult(PlatformAction.LAUNCH_GAME, game_id="color_wars")

    assert result.game_id == "color_wars"

