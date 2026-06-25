"""Capabilities a mini-game can request from the platform."""

from enum import Enum


class GameCapability(str, Enum):
    """Optional capabilities advertised by games."""

    LOCAL_PLAY = "local_play"
    ONLINE_MULTIPLAYER = "online_multiplayer"
    OASIS_IDENTITY = "oasis_identity"
    CONFIDENTIAL_MATCH = "confidential_match"
    VERIFIED_RESULT = "verified_result"
    PLATFORM_ACHIEVEMENT = "platform_achievement"
