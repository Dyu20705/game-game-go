"""Application composition root.

This module is the one platform layer allowed to import public game adapters.
Runtime platform scenes and services should depend on `src.platform.games`
contracts instead of game internals.
"""

from pathlib import Path

from src.games.color_wars.game import ColorWarsGame
from src.games.demo_game.game import DemoGame
from src.games.nuts_and_bolts.game import NutsAndBoltsGame
from src.games.square_xo.game import SquareXOGame
from src.platform.blockchain.adapters.local import LocalIdentity, LocalMatchRegistry, LocalResultVerifier
from src.platform.blockchain.config import OasisNetworkConfig
from src.platform.blockchain.services.blockchain_service import BlockchainService
from src.platform.config import PlatformConfig
from src.platform.context import PlatformContext
from src.platform.games import GameRegistry
from src.platform.services import AssetService, AudioService, LocalizationService, SaveService, SettingsService


def build_default_registry() -> GameRegistry:
    """Create the static registry used by the current platform build."""

    registry = GameRegistry()
    for game in (ColorWarsGame(), SquareXOGame(), NutsAndBoltsGame(), DemoGame()):
        registry.register(game)
    return registry


def build_platform_context(pygame, config: PlatformConfig, registry: GameRegistry) -> PlatformContext:
    """Wire runtime services and adapters for the app shell."""

    save = SaveService(config.save_path)
    settings = SettingsService.from_document(save.load())
    localization = LocalizationService(settings.platform.language)
    assets = AssetService(config.repository_root)
    audio = AudioService(settings)
    chain_config = OasisNetworkConfig.from_environment()
    verifier = LocalResultVerifier()
    for game in registry.list_enabled():
        register_verifiers = getattr(game, "register_verifiers", None)
        if register_verifiers is not None:
            register_verifiers(verifier)

    blockchain = BlockchainService(
        config=chain_config,
        identity=LocalIdentity(),
        match_registry=LocalMatchRegistry(),
        result_verifier=verifier,
    )
    audio_dir = assets.audio("")
    if audio_dir.exists():
        audio.set_music_paths(sorted(Path(audio_dir).glob("*.mp3")))

    flags = pygame.FULLSCREEN if settings.platform.fullscreen else pygame.RESIZABLE
    screen = pygame.display.set_mode(settings.platform.window_size, flags)
    pygame.display.set_caption(config.app_name)
    try:
        pygame.display.set_icon(assets.image(pygame, assets.brand("app_icon.png"), fallback_size=(64, 64)))
    except pygame.error:
        pass
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
