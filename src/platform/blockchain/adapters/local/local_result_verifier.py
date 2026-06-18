"""Local deterministic replay verifier."""

from collections.abc import Callable

from src.platform.blockchain.domain.result import ReplayVerificationRequest, VerificationResult


class LocalResultVerifier:
    """Dispatch replay verification by game id."""

    def __init__(self):
        self._verifiers: dict[str, Callable[[ReplayVerificationRequest], VerificationResult]] = {}

    def register(self, game_id: str, verifier: Callable[[ReplayVerificationRequest], VerificationResult]):
        self._verifiers[game_id] = verifier

    def verify_replay(self, request: ReplayVerificationRequest) -> VerificationResult:
        verifier = self._verifiers.get(request.envelope.game_id)
        if verifier is None:
            return VerificationResult(False, reason="unknown_game")
        return verifier(request)

