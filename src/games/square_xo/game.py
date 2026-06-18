"""Game Game Go adapter for SquareXO."""

from src.platform.games import GameLaunchOptions

from .manifest import DESCRIPTOR
from .runtime.local_session import SquareXOLocalSession
from .view.launch_scene import run_square_xo_launch_scene


class SquareXOGame:
    @property
    def descriptor(self):
        return DESCRIPTOR

    def configure_launch(self, context) -> GameLaunchOptions | None:
        return run_square_xo_launch_scene(context)

    def create_session(self, context, launch_options: GameLaunchOptions):
        custom = dict(launch_options.custom)
        custom.setdefault("rows", 4)
        custom.setdefault("cols", 4)
        custom.setdefault("stake_mode", "NO_STAKE")
        custom.setdefault("blockchain_mode", "LOCAL_MOCK")
        return SquareXOLocalSession(
            context=context,
            launch_options=GameLaunchOptions(mode="local_1v1", custom=custom),
        )

