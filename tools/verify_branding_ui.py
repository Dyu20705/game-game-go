"""Verify branded menu assets and layout across common desktop resolutions."""

from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace

RESOLUTIONS = ((1280, 720), (1366, 768), (1600, 900), (1920, 1080))


def main() -> int:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

    import pygame

    from src.platform.scenes.home_scene import _compute_home_layout, _draw_brand_panel, _draw_home_background
    from src.platform.services import AssetService

    pygame.init()
    try:
        assets = AssetService(Path.cwd())
        for width, height in RESOLUTIONS:
            screen = pygame.display.set_mode((width, height))
            context = SimpleNamespace(screen=screen, assets=assets)
            _draw_home_background(pygame, screen, context)
            layout = _compute_home_layout(pygame, width, height, 4)
            body_font = assets.font(pygame, "body", 17)
            small_font = assets.font(pygame, "body", 13)
            _draw_brand_panel(pygame, screen, context, layout, pygame.time.get_ticks() - 240, body_font, small_font)
            _assert_layout(width, height, layout)
            pygame.display.flip()
    finally:
        pygame.quit()

    print("Branding UI verification passed")
    return 0


def _assert_layout(width: int, height: int, layout: dict[str, object]) -> None:
    panel = layout["panel"]
    buttons = layout["buttons"]
    logo_box = layout["logo_box"]
    safe_x = int(width * 0.05)
    safe_y = int(height * 0.05)
    screen_rect = panel.__class__(0, 0, width, height)
    if not screen_rect.contains(panel):
        raise RuntimeError(f"panel outside screen at {width}x{height}: {panel}")
    if panel.x < safe_x and width >= 900:
        raise RuntimeError(f"panel violates horizontal safe area at {width}x{height}: {panel}")
    if panel.y < safe_y:
        raise RuntimeError(f"panel violates vertical safe area at {width}x{height}: {panel}")
    if not panel.contains(logo_box):
        raise RuntimeError(f"logo box outside panel at {width}x{height}: {logo_box}")
    previous_bottom = 0
    for button in buttons:
        if not panel.contains(button):
            raise RuntimeError(f"button outside panel at {width}x{height}: {button}")
        if button.height < 44:
            raise RuntimeError(f"button hit area too small at {width}x{height}: {button}")
        if previous_bottom and button.y <= previous_bottom:
            raise RuntimeError(f"button order overlaps at {width}x{height}: {button}")
        previous_bottom = button.bottom


if __name__ == "__main__":
    raise SystemExit(main())
