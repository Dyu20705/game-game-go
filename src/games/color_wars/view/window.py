"""Window creation and display management."""

from pathlib import Path

import pygame

from .constants import DEFAULT_HEIGHT, DEFAULT_WIDTH

_ICON_SURFACE = None


def _load_window_icon():
    """Load window icon from assets once."""
    global _ICON_SURFACE
    if _ICON_SURFACE is not None:
        return _ICON_SURFACE

    icon_path = Path(__file__).resolve().parents[4] / "assets" / "brand" / "app_icon.png"
    try:
        _ICON_SURFACE = pygame.image.load(str(icon_path)).convert_alpha()
    except (pygame.error, FileNotFoundError, OSError):
        _ICON_SURFACE = None
    return _ICON_SURFACE


def drawScreen(fullscreen=False, size=(DEFAULT_WIDTH, DEFAULT_HEIGHT)):
    """Create or recreate the game window.
    
    Args:
        fullscreen: bool, if True create fullscreen display
        size: (width, height) for windowed mode
        
    Returns:
        pygame display surface
    """
    flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
    screen_size = (0, 0) if fullscreen else size
    screen = pygame.display.set_mode(screen_size, flags)
    pygame.display.set_caption("Color Wars")
    icon = _load_window_icon()
    if icon is not None:
        pygame.display.set_icon(icon)
    return screen


def toggle_fullscreen(is_fullscreen, screen):
    """Toggle between fullscreen and windowed mode.
    
    Args:
        is_fullscreen: current fullscreen state
        screen: pygame display surface
        
    Returns:
        (new_screen, new_is_fullscreen) tuple
    """
    if is_fullscreen:
        return drawScreen(fullscreen=False), False
    return drawScreen(fullscreen=True), True


