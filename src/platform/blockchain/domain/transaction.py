"""Transaction receipt domain types."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SubmissionReceipt:
    submitted: bool
    reference: str
    tx_hash: str | None = None
    message: str | None = None
