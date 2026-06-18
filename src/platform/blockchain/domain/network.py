"""Network health domain types."""

from dataclasses import dataclass
from enum import Enum


class ChainHealthStatus(str, Enum):
    NOT_CONFIGURED = "not_configured"
    CONNECTED = "connected"
    UNAVAILABLE = "unavailable"


@dataclass(frozen=True)
class ChainHealth:
    sapphire: ChainHealthStatus
    rofl: ChainHealthStatus
    mode: str
    message: str | None = None

