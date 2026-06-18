"""Achievement port."""

from typing import Protocol


class AchievementPort(Protocol):
    def record_achievement(self, identity_id: str, achievement_id: str, evidence_hash: str) -> bool:
        ...

