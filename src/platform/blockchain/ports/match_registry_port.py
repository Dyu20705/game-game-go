"""Match registry port."""

from typing import Protocol

from src.platform.blockchain.domain.match import CreateMatchRequest, MatchRecord, MatchReference
from src.platform.blockchain.domain.result import MatchEnvelope
from src.platform.blockchain.domain.transaction import SubmissionReceipt


class MatchRegistryPort(Protocol):
    def create_match(self, request: CreateMatchRequest) -> MatchReference: ...

    def get_match(self, match_id: str) -> MatchRecord | None: ...

    def submit_result(self, envelope: MatchEnvelope) -> SubmissionReceipt: ...
