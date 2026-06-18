"""Runtime context passed from the platform into mini-games."""

from dataclasses import dataclass
from typing import Any


@dataclass
class PlatformContext:
    """Shared services and runtime objects available to mini-games."""

    screen: Any
    clock: Any
    settings: Any
    audio: Any
    assets: Any
    save: Any
    localization: Any
    logger: Any = None

