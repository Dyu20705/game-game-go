"""Minimal scene manager for blocking transitional scenes."""


class SceneManager:
    """Track the current platform scene name."""

    def __init__(self, initial: str = "home"):
        self.current = initial

    def go_to(self, scene_name: str):
        self.current = scene_name

