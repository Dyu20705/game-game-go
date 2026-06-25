"""Match registry domain types."""

from dataclasses import dataclass
from enum import Enum


class MatchStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class PlayerRef:
    player_id: str
    display_name: str
    address: str | None = None


@dataclass(frozen=True)
class CreateMatchRequest:
    game_id: str
    ruleset_version: str
    players: tuple[PlayerRef, ...]
    stake_mode: str = "NO_STAKE"


@dataclass(frozen=True)
class MatchReference:
    match_id: str
    game_id: str
    ruleset_version: str


@dataclass(frozen=True)
class MatchRecord:
    reference: MatchReference
    status: MatchStatus
    players: tuple[PlayerRef, ...]
    result_hash: str | None = None
