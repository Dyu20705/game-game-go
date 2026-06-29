"""Game Game Go shell using the focused arcade shelf as its home."""

from src.platform.bootstrap import build_default_registry, build_platform_context
from src.platform.config import PlatformConfig
from src.platform.games import GameExitAction, GameLaunchOptions, GameRegistry
from src.platform.scenes.arcade_shelf_scene import run_arcade_shelf_scene
from src.platform.scenes.base import PlatformAction
from src.platform.scenes.game_details_scene import run_about_scene
from src.platform.scenes.leaderboard_scene import run_leaderboard_scene
from src.platform.scenes.rewards_scene import run_rewards_scene
from src.platform.scenes.settings_scene import run_settings_scene
from src.platform.scenes.studio_intro_scene import run_studio_intro_scene


class FocusedPlatformApp:
    """Blocking platform shell with a single game-first home surface."""

    def __init__(self, config: PlatformConfig | None = None, registry: GameRegistry | None = None):
        self.config = config or PlatformConfig()
        self.registry = registry or build_default_registry()

    def _build_context(self, pygame):
        return build_platform_context(pygame, self.config, self.registry)

    def run(self) -> int:
        import pygame

        pygame.init()
        context = self._build_context(pygame)
        run_studio_intro_scene(pygame, context)
        context.audio.play_menu_music()
        scene = PlatformAction.HOME

        try:
            while scene != PlatformAction.QUIT:
                if scene in (PlatformAction.HOME, PlatformAction.GAME_LIBRARY):
                    result = run_arcade_shelf_scene(pygame, context, self.registry)
                elif scene == PlatformAction.SETTINGS:
                    result = run_settings_scene(pygame, context)
                elif scene == PlatformAction.ABOUT:
                    result = run_about_scene(pygame, context)
                elif scene == PlatformAction.LEADERBOARD:
                    result = run_leaderboard_scene(pygame, context)
                elif scene == PlatformAction.REWARDS:
                    result = run_rewards_scene(pygame, context)
                else:
                    result = run_arcade_shelf_scene(pygame, context, self.registry)

                if result.action == PlatformAction.LAUNCH_GAME and result.game_id:
                    game = self.registry.get(result.game_id)
                    options = self._configure_launch(game, context)
                    if options is None:
                        scene = PlatformAction.GAME_LIBRARY
                        continue
                    exit_result = game.create_session(context, options).run()
                    if exit_result.action == GameExitAction.QUIT:
                        scene = PlatformAction.QUIT
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
    """Run the focused Game Game Go experience."""

    return FocusedPlatformApp().run()
