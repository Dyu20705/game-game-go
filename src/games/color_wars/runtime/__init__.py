"""Color Wars runtime package exports."""

from .state import GameState

__all__ = ["CoreSystems", "GameState", "LaunchConfig", "SceneName", "run_game"]


def __getattr__(name):
    if name == "run_game":
        from .loop import run_game

        return run_game
    if name in {"CoreSystems", "LaunchConfig", "SceneName"}:
        from .core import CoreSystems, LaunchConfig, SceneName

        return {"CoreSystems": CoreSystems, "LaunchConfig": LaunchConfig, "SceneName": SceneName}[name]
    raise AttributeError(name)


