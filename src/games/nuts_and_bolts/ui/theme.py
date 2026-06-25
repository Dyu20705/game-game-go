from __future__ import annotations

import pygame

FPS = 60
MIN_SIZE = (900, 620)
DEFAULT_SIZE = (1000, 680)

BACKGROUND = (232, 228, 218)
SURFACE = (248, 246, 239)
SURFACE_DARK = (221, 217, 206)
TEXT = (42, 41, 38)
MUTED_TEXT = (97, 93, 84)
BORDER = (168, 163, 150)
METAL = (105, 108, 112)
METAL_DARK = (74, 76, 80)
METAL_LIGHT = (184, 188, 190)
HOLE = (54, 55, 57)
SPARE = (138, 140, 142)
SELECT = (248, 193, 65)
VALID = (91, 159, 115)
ERROR = (204, 76, 65)
SUCCESS = (76, 154, 101)
SHADOW = (0, 0, 0, 42)

PALETTE: dict[str, tuple[int, int, int]] = {
    "red": (218, 79, 76),
    "blue": (64, 129, 207),
    "yellow": (229, 184, 61),
    "green": (72, 166, 103),
    "purple": (143, 89, 188),
    "orange": (224, 128, 57),
}


def font(size: int, *, bold: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(["segoeui", "arial", "dejavusans"], size, bold=bold)


def lighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, channel + amount) for channel in color)


def darken(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(max(0, channel - amount) for channel in color)
