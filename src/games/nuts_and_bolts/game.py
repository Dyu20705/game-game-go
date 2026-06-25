"""Game Game Go adapter for Nuts & Bolts."""

from src.platform.context import PlatformContext
from src.platform.games import GameDescriptor, GameLaunchOptions

from .manifest import DESCRIPTOR
from .session import NutsAndBoltsSession


class NutsAndBoltsGame:
    """Registered Nuts & Bolts game module."""

    @property
    def descriptor(self) -> GameDescriptor:
        return DESCRIPTOR

    def create_session(
        self,
        context: PlatformContext,
        launch_options: GameLaunchOptions,
    ) -> NutsAndBoltsSession:
        return NutsAndBoltsSession(context=context, launch_options=launch_options)
