"""Result verifier port."""

from typing import Protocol

from src.platform.blockchain.domain.result import ReplayVerificationRequest, VerificationResult


class ResultVerifierPort(Protocol):
    def verify_replay(self, request: ReplayVerificationRequest) -> VerificationResult:
        ...

