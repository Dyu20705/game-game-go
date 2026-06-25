"""Asset loading helpers for the view layer."""

from pathlib import Path

import pygame


ASSETS_ROOT = Path(__file__).resolve().parents[3] / "assets" / "games" / "color_wars"


def get_asset_path(*parts):
    """Return an absolute Color Wars asset path under assets/."""
    return ASSETS_ROOT.joinpath(*parts)


def get_home_asset_path(filename):
    """Resolve a home asset from the new image/gameplay layout or fallback to root."""
    for folder in ("images", "gameplay", "home"):
        candidate = ASSETS_ROOT / folder / filename
        if candidate.exists():
            return candidate
    return ASSETS_ROOT / filename


def load_image(path, size=None, alpha=True):
    """Load an image and optionally scale it.

    Raises pygame.error/FileNotFoundError when loading fails.
    """
    surface = pygame.image.load(str(path))
    surface = surface.convert_alpha() if alpha else surface.convert()
    if size is not None:
        surface = pygame.transform.smoothscale(surface, size)
    return surface


def load_icon_or_placeholder(path, size, color):
    """Load icon image; fallback to a colored circular placeholder."""
    try:
        return load_image(path, size=size, alpha=True)
    except (pygame.error, FileNotFoundError, OSError):
        surface = pygame.Surface(size, pygame.SRCALPHA)
        center = (size[0] // 2, size[1] // 2)
        radius = min(size[0], size[1]) // 2 - 2
        pygame.draw.circle(surface, color, center, radius)
        pygame.draw.circle(surface, (255, 255, 255), center, max(2, radius // 3), 2)
        return surface
