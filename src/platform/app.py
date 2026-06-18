"""Game Game Go platform application shell."""

from pathlib import Path

from src.games.color_wars.game import ColorWarsGame
from src.games.demo_game.game import DemoGame
from src.games.square_xo.game import SquareXOGame
from src.games.square_xo.application.result_submission import verify_square_xo_replay
from src.platform.blockchain.config import OasisNetworkConfig
from src.platform.blockchain.adapters.local import LocalIdentity, LocalMatchRegistry, LocalResultVerifier
from src.platform.blockchain.services.blockchain_service import BlockchainService
from src.platform.config import PlatformConfig
from src.platform.context import PlatformContext
from src.platform.games import GameExitAction, GameLaunchOptions, GameRegistry
from src.platform.scenes.base import PlatformAction
from src.platform.scenes.game_details_scene import run_about_scene
from src.platform.scenes.home_scene import run_home_scene
from src.platform.scenes.leaderboard_scene import run_leaderboard_scene
from src.platform.scenes.library_scene import run_library_scene
from src.platform.scenes.rewards_scene import run_rewards_scene
from src.platform.scenes.settings_scene import run_settings_scene
from src.platform.services import AssetService, AudioService, LocalizationService, SaveService, SettingsService


def build_default_registry() -> GameRegistry:
    """Create the static registry used by the current platform build."""

    registry = GameRegistry()
    registry.register(ColorWarsGame())
    registry.register(SquareXOGame())
    registry.register(DemoGame())
    return registry


class PlatformApp:
    """Blocking transitional platform shell for Game Game Go."""

    def __init__(self, config: PlatformConfig | None = None, registry: GameRegistry | None = None):
        self.config = config or PlatformConfig()
        self.registry = registry or build_default_registry()

    def _build_context(self, pygame):
        save = SaveService(self.config.save_path)
        settings = SettingsService.from_document(save.load())
        localization = LocalizationService(settings.platform.language)
        assets = AssetService(self.config.repository_root)
        audio = AudioService(settings)
        chain_config = OasisNetworkConfig.from_environment()
        verifier = LocalResultVerifier()
        verifier.register("square_xo", verify_square_xo_replay)
        blockchain = BlockchainService(
            config=chain_config,
            identity=LocalIdentity(),
            match_registry=LocalMatchRegistry(),
            result_verifier=verifier,
        )
        audio_dir = self.config.repository_root / "asset" / "aud"
        if audio_dir.exists():
            audio.set_music_paths(sorted(Path(audio_dir).glob("*.mp3")))

        flags = pygame.FULLSCREEN if settings.platform.fullscreen else pygame.RESIZABLE
        screen = pygame.display.set_mode(settings.platform.window_size, flags)
        pygame.display.set_caption(self.config.app_name)
        clock = pygame.time.Clock()
        return PlatformContext(
            screen=screen,
            clock=clock,
            settings=settings,
            audio=audio,
            assets=assets,
            save=save,
            localization=localization,
            blockchain=blockchain,
        )

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
