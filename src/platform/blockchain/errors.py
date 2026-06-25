"""Typed blockchain errors mapped away from raw RPC/SDK failures."""

from enum import Enum


class BlockchainErrorCode(str, Enum):
    NETWORK_UNAVAILABLE = "network_unavailable"
    USER_REJECTED = "user_rejected"
    TRANSACTION_PENDING = "transaction_pending"
    TRANSACTION_REVERTED = "transaction_reverted"
    CONTRACT_NOT_CONFIGURED = "contract_not_configured"
    INVALID_NETWORK = "invalid_network"
    ROFL_UNAVAILABLE = "rofl_unavailable"
    VERIFICATION_FAILED = "verification_failed"
    INVALID_LIFECYCLE = "invalid_lifecycle"


class BlockchainError(RuntimeError):
    """Platform-level blockchain failure."""

    def __init__(self, code: BlockchainErrorCode, message: str):
        super().__init__(message)
        self.code = code
