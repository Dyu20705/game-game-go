"""Headless smoke test for local and Docker environments."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from types import SimpleNamespace


def main() -> int:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    os.environ.setdefault("BLOCKCHAIN_MODE", "local")

    import pygame

    from src.games.color_wars.engine.rules import PLAYER_BLUE
    from src.games.color_wars.runtime.state import GameState
    from src.games.color_wars.view.gameplay_scene.scene import draw_gameplay_scene
    from src.games.square_xo.domain.board import create_game
    from src.games.square_xo.view.gameplay_scene import draw_gameplay
    from src.platform.bootstrap import build_default_registry
    from src.platform.config import PlatformConfig
    from src.platform.games import GameLaunchOptions
    from src.platform.scenes.studio_intro_scene import run_studio_intro_scene
    from src.platform.services import AssetService

    temp_root = Path(".test_tmp")
    temp_root.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="game-game-go-smoke-", dir=temp_root))
    try:
        config = PlatformConfig(save_path=tmp / "settings.json")
        registry = build_default_registry()
        games = {game.descriptor.game_id: game for game in registry.list_enabled()}
        required = {"color_wars", "square_xo", "nuts_and_bolts"}
        missing = required - set(games)
        if missing:
            raise RuntimeError(f"missing registered games: {sorted(missing)}")

        pygame.init()
        try:
            screen = pygame.display.set_mode((960, 540))
            assets = AssetService(config.repository_root)
            icon = assets.image(pygame, assets.brand("app_icon.png"), fallback_size=(64, 64))
            if icon.get_width() <= 0 or icon.get_height() <= 0:
                raise RuntimeError("brand icon failed to load")
            logo = assets.image(pygame, assets.branding("game_logo_full_runtime.png"), fallback_size=(320, 180))
            studio = assets.image(pygame, assets.branding("studio_logo_runtime.png"), fallback_size=(160, 160))
            background = assets.cover_image(
                pygame, assets.background("menu_background_1920x1080.png"), screen.get_size()
            )
            if logo.get_width() < 200 or studio.get_width() < 100 or background.get_size() != screen.get_size():
                raise RuntimeError("branding assets failed to load")
            run_studio_intro_scene(pygame, _SmokeContext(screen, assets=assets), duration_ms=250)

            state = GameState()
            draw_gameplay_scene(
                screen,
                state,
                state.board,
                state.dots,
                PLAYER_BLUE,
                0,
                0,
                None,
                "pvbot",
                "easy",
            )

            square_state = create_game(rows=2, cols=2)
            draw_gameplay(pygame, screen, square_state, None, "Local smoke")

            for game_id in sorted(required):
                game = games[game_id]
                session = game.create_session(_SmokeContext(screen, assets=assets), GameLaunchOptions())
                if not hasattr(session, "run"):
                    raise RuntimeError(f"{game_id} session has no run()")
        finally:
            pygame.quit()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("Game Game Go smoke test passed")
    return 0


class _SmokeContext:
    def __init__(self, screen, assets=None):
        self.screen = screen
        self.clock = _SmokeClock()
        self.settings = _SmokeSettings()
        self.audio = SimpleNamespace(toggle_music=lambda: None, update=lambda: None)
        self.assets = assets
        self.save = None
        self.localization = SimpleNamespace(get=lambda key: key, set_language=lambda _language: None)
        self.blockchain = None


class _SmokeClock:
    def tick(self, _fps: int) -> None:
        return None


class _SmokeSettings:
    def __init__(self) -> None:
        self.platform = SimpleNamespace(
            sound_enabled=False,
            master_volume=0.0,
            fullscreen=False,
            language="en",
            set_master_volume=lambda _volume: None,
        )
        self._games: dict[str, dict[str, str]] = {}

    def get_game_settings(self, game_id: str) -> dict[str, str]:
        return dict(self._games.get(game_id, {}))

    def update_game_settings(self, game_id: str, values: dict[str, str]) -> None:
        self._games.setdefault(game_id, {}).update(values)


if __name__ == "__main__":
    raise SystemExit(main())
