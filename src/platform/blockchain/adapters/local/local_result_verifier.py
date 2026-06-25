"""Local deterministic replay verifier."""

from collections.abc import Callable

from src.platform.blockchain.domain.result import ReplayVerificationRequest, VerificationResult
from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


class LocalResultVerifier:
    """Dispatch replay verification by game id."""

    def __init__(self):
        self._verifiers: dict[str, Callable[[ReplayVerificationRequest], VerificationResult]] = {}

    def register(self, game_id: str, verifier: Callable[[ReplayVerificationRequest], VerificationResult]):
        if game_id in self._verifiers:
            raise BlockchainError(BlockchainErrorCode.INVALID_LIFECYCLE, f"verifier already registered: {game_id}")
        self._verifiers[game_id] = verifier

    def supported_games(self) -> tuple[str, ...]:
        return tuple(sorted(self._verifiers))

    def verify_replay(self, request: ReplayVerificationRequest) -> VerificationResult:
        verifier = self._verifiers.get(request.envelope.game_id)
        if verifier is None:
            return VerificationResult(False, reason="unknown_game")
        return verifier(request)
