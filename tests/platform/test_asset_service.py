import os
from pathlib import Path

os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from src.games.color_wars.manifest import DESCRIPTOR as COLOR_WARS
from src.games.nuts_and_bolts.manifest import DESCRIPTOR as NUTS_AND_BOLTS
from src.games.square_xo.manifest import DESCRIPTOR as SQUARE_XO
from src.platform.services import AssetService


def test_asset_service_resolves_canonical_namespaces(tmp_path):
    service = AssetService(Path(tmp_path))

    assert service.brand("logo_mark.png") == tmp_path / "assets" / "brand" / "logo_mark.png"
    assert (
        service.platform("fallbacks/game_thumbnail.png")
        == tmp_path / "assets" / "platform" / "fallbacks" / "game_thumbnail.png"
    )
    assert service.audio("theme.mp3") == tmp_path / "assets" / "audio" / "theme.mp3"
    assert (
        service.game("color_wars", "images/game_icon.png")
        == tmp_path / "assets" / "games" / "color_wars" / "images" / "game_icon.png"
    )


def test_legacy_shim_maps_to_assets_not_old_asset_root(tmp_path):
    service = AssetService(Path(tmp_path))

    assert service.legacy("aud/song.mp3") == tmp_path / "assets" / "audio" / "song.mp3"
    assert (
        service.legacy("img/color-wars/game_icon.png")
        == tmp_path / "assets" / "games" / "color_wars" / "images" / "game_icon.png"
    )


def test_missing_image_returns_placeholder_surface(tmp_path):
    pygame.init()
    try:
        service = AssetService(Path(tmp_path))
        surface = service.image(pygame, service.game("missing", "thumbnail.png"), fallback_size=(80, 45))
        assert surface.get_size() == (80, 45)
    finally:
        pygame.quit()


def test_scaled_image_cache_is_bounded_and_reused():
    pygame.init()
    try:
        service = AssetService(Path.cwd(), max_scaled_images=2)
        image = service.scaled_image(pygame, COLOR_WARS.thumbnail, (160, 90))
        again = service.scaled_image(pygame, COLOR_WARS.thumbnail, (160, 90))
        service.scaled_image(pygame, SQUARE_XO.thumbnail, (160, 90))
        service.scaled_image(pygame, NUTS_AND_BOLTS.thumbnail, (160, 90))

        assert image is again
        assert service.stats.scaled_hits >= 1
        assert service.cache_sizes()["scaled_images"] == 2
    finally:
        pygame.quit()


def test_font_cache_reuses_font_object():
    pygame.init()
    try:
        service = AssetService(Path.cwd())
        font = service.font(pygame, "body", 16, bold=True)
        again = service.font(pygame, "body", 16, bold=True)

        assert font is again
        assert service.stats.font_hits == 1
    finally:
        pygame.quit()


def test_registered_games_declare_thumbnails():
    for descriptor in (COLOR_WARS, SQUARE_XO, NUTS_AND_BOLTS):
        assert descriptor.thumbnail is not None
        assert AssetService(Path.cwd()).resolve(descriptor.thumbnail).exists()


def test_legacy_asset_root_is_not_present():
    assert not (Path.cwd() / "asset").exists()
