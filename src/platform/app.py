"""Game Game Go platform application shell."""

from src.platform.bootstrap import build_default_registry, build_platform_context
from src.platform.config import PlatformConfig
from src.platform.games import GameExitAction, GameLaunchOptions, GameRegistry
from src.platform.scenes.base import PlatformAction
from src.platform.scenes.game_details_scene import run_about_scene
from src.platform.scenes.home_scene import run_home_scene
from src.platform.scenes.leaderboard_scene import run_leaderboard_scene
from src.platform.scenes.library_scene import run_library_scene
from src.platform.scenes.rewards_scene import run_rewards_scene
from src.platform.scenes.settings_scene import run_settings_scene


class PlatformApp:
    """Blocking transitional platform shell for Game Game Go."""

    def __init__(self, config: PlatformConfig | None = None, registry: GameRegistry | None = None):
        self.config = config or PlatformConfig()
        self.registry = registry or build_default_registry()

    def _build_context(self, pygame):
        return build_platform_context(pygame, self.config, self.registry)

    def run(self) -> int:
        import pygame

        pygame.init()
        context = self._build_context(pygame)
        context.audio.play_menu_music()
        scene = PlatformAction.HOME

        try:
            while scene != PlatformAction.QUIT:
                if scene == PlatformAction.HOME:
                    result = run_home_scene(pygame, context)
                elif scene == PlatformAction.GAME_LIBRARY:
                    result = run_library_scene(pygame, context, self.registry)
                elif scene == PlatformAction.SETTINGS:
                    result = run_settings_scene(pygame, context)
                elif scene == PlatformAction.ABOUT:
                    result = run_about_scene(pygame, context)
                elif scene == PlatformAction.LEADERBOARD:
                    result = run_leaderboard_scene(pygame, context)
                elif scene == PlatformAction.REWARDS:
                    result = run_rewards_scene(pygame, context)
                else:
                    result = run_home_scene(pygame, context)

                if result.action == PlatformAction.LAUNCH_GAME and result.game_id:
                    game = self.registry.get(result.game_id)
                    options = self._configure_launch(game, context)
                    if options is None:
                        scene = PlatformAction.GAME_LIBRARY
                        continue
                    exit_result = game.create_session(context, options).run()
                    if exit_result.action == GameExitAction.QUIT:
                        scene = PlatformAction.QUIT
                    elif exit_result.action == GameExitAction.HOME:
                        scene = PlatformAction.HOME
                    elif exit_result.action == GameExitAction.RESTART:
                        scene = PlatformAction.GAME_LIBRARY
                    else:
                        scene = PlatformAction.GAME_LIBRARY
                    context.audio.play_menu_music()
                else:
                    scene = result.action
        finally:
            context.save.save(context.settings.to_document())
            pygame.quit()
        return 0

    @staticmethod
    def _configure_launch(game, context):
        configure = getattr(game, "configure_launch", None)
        if configure is None:
            return GameLaunchOptions()
        return configure(context)


def main() -> int:
    """Run the default Game Game Go app."""

    return PlatformApp().run()
