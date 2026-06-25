"""Map Oasis adapter exceptions to typed platform errors."""

from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


def map_exception(error: Exception) -> BlockchainError:
    message = str(error)
    lowered = message.lower()
    if "reject" in lowered:
        return BlockchainError(BlockchainErrorCode.USER_REJECTED, message)
    if "timeout" in lowered:
        return BlockchainError(BlockchainErrorCode.NETWORK_UNAVAILABLE, message)
    if "revert" in lowered:
        return BlockchainError(BlockchainErrorCode.TRANSACTION_REVERTED, message)
    return BlockchainError(BlockchainErrorCode.NETWORK_UNAVAILABLE, message)
