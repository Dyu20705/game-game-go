"""Protocol-based contract between the platform and mini-games."""

from typing import Protocol

from src.platform.context import PlatformContext

from .descriptor import GameDescriptor
from .launch import GameExitResult, GameLaunchOptions


class GameSession(Protocol):
    """A running mini-game session."""

    def run(self) -> GameExitResult:
        """Run until the mini-game returns control to the platform."""


class GameModule(Protocol):
    """A registered mini-game module.

    Protocol keeps the contract lightweight: games do not have to inherit from a
    framework base class, but static type checkers and tests can still verify the
    public shape.
    """

    @property
    def descriptor(self) -> GameDescriptor:
        """Return stable metadata for registry and library UI."""

    def create_session(
        self,
        context: PlatformContext,
        launch_options: GameLaunchOptions,
    ) -> GameSession:
        """Create a session for the supplied launch options."""

