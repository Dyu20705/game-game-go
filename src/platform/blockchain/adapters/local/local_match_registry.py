"""In-memory match registry for offline/local mode."""

from dataclasses import replace
from itertools import count

from src.platform.blockchain.domain.commitment import result_commitment_for_envelope
from src.platform.blockchain.domain.match import CreateMatchRequest, MatchRecord, MatchReference, MatchStatus
from src.platform.blockchain.domain.result import MatchEnvelope
from src.platform.blockchain.domain.transaction import SubmissionReceipt
from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


class LocalMatchRegistry:
    """Real local implementation used by app/tests without network."""

    def __init__(self):
        self._counter = count(1)
        self._records: dict[str, MatchRecord] = {}

    def create_match(self, request: CreateMatchRequest) -> MatchReference:
        match_id = f"local-{next(self._counter)}"
        reference = MatchReference(match_id=match_id, game_id=request.game_id, ruleset_version=request.ruleset_version)
        self._records[match_id] = MatchRecord(reference=reference, status=MatchStatus.CREATED, players=request.players)
        return reference

    def get_match(self, match_id: str) -> MatchRecord | None:
        return self._records.get(match_id)

    def submit_result(self, envelope: MatchEnvelope) -> SubmissionReceipt:
        record = self._records.get(envelope.match_id)
        if record is None:
            reference = MatchReference(envelope.match_id, envelope.game_id, envelope.ruleset_version)
            record = MatchRecord(reference=reference, status=MatchStatus.CREATED, players=tuple())
        if record.status in {MatchStatus.RESOLVED, MatchStatus.CANCELLED}:
            raise BlockchainError(BlockchainErrorCode.INVALID_LIFECYCLE, "match is already finalized")
        result_hash = result_commitment_for_envelope(envelope)
        self._records[envelope.match_id] = replace(record, status=MatchStatus.RESOLVED, result_hash=result_hash)
        return SubmissionReceipt(submitted=True, reference=envelope.match_id, tx_hash=None, message=result_hash)
