"""Base scene class and scene lifecycle management."""

from abc import ABC, abstractmethod


class BaseScene(ABC):
    """Abstract base class for all game scenes.

    Enforces consistent interface for scene lifecycle and rendering.
    Subclasses must implement render() and handle_event().
    """

    def __init__(self):
        """Initialize scene state."""
        self._initialized = False

    def initialize(self):
        """Called once when scene becomes active. Load assets here."""
        self._initialized = True

    def deinitialize(self):
        """Called when scene becomes inactive. Clean up here."""
        self._initialized = False

    @abstractmethod
    def render(self, screen, **kwargs):
        """Render the scene to screen.

        Args:
            screen: pygame display surface
            **kwargs: scene-specific rendering context
        """
        pass

    @abstractmethod
    def handle_event(self, event, **kwargs):
        """Process pygame event.

        Args:
            event: pygame.event.Event
            **kwargs: scene-specific event context

        Returns:
            bool indicating if event was handled
        """
        pass


class SceneController:
    """Manages active scene and transitions.

    Provides a simple state machine for scene management with
    automatic initialization/deinitialization.
    """

    def __init__(self):
        """Initialize scene controller."""
        self._current_scene: BaseScene | None = None

    def set_scene(self, scene: BaseScene):
        """Transition to a new scene.

        Args:
            scene: BaseScene subclass instance
        """
        if self._current_scene:
            self._current_scene.deinitialize()
        self._current_scene = scene
        if scene:
            scene.initialize()

    def render(self, screen, **kwargs):
        """Render active scene."""
        if self._current_scene:
            self._current_scene.render(screen, **kwargs)

    def handle_event(self, event, **kwargs):
        """Handle event in active scene."""
        if self._current_scene:
            return self._current_scene.handle_event(event, **kwargs)
        return False

    def get_current_scene(self) -> BaseScene | None:
        """Get currently active scene."""
        return self._current_scene
