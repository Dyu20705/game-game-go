"""Visual effects used by the game board."""

import pygame

from src.games.color_wars.engine.rules import PLAYER_BLUE

from ..constants import BLUE_COLOR, RED_COLOR
from ..layout import _cell_center


def drawExplosionOverlay(screen, layout, step, progress):
    """Draw the explosion animation for the current step."""
    if step is None:
        return

    center = step.get("center")
    targets = step.get("targets", [])
    owner = step.get("owner")
    if center is None:
        return

    base_color = BLUE_COLOR if owner == PLAYER_BLUE else RED_COLOR
    glow = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    cx, cy = _cell_center(layout, center[0], center[1])
    cell_size = layout["cell_size"]

    ring_radius = int(max(8, cell_size * (0.2 + 0.55 * progress)))
    ring_width = max(2, int(cell_size * 0.08))
    ring_alpha = max(0, int(190 * (1.0 - progress)))
    pygame.draw.circle(glow, (*base_color, ring_alpha), (cx, cy), ring_radius, ring_width)

    dot_radius = max(3, int(cell_size * 0.09))
    travel_alpha = max(0, int(220 * (1.0 - progress * 0.6)))
    for tr, tc in targets:
        tx, ty = _cell_center(layout, tr, tc)
        px = int(cx + (tx - cx) * progress)
        py = int(cy + (ty - cy) * progress)
        pygame.draw.circle(glow, (*base_color, travel_alpha), (px, py), dot_radius)

    screen.blit(glow, (0, 0))

