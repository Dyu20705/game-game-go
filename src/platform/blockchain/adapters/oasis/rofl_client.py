"""ROFL client configuration guard."""

from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


class RoflClient:
    def __init__(self, config):
        self.config = config

    def require_configured(self):
        if not self.config.rofl_service_url:
            raise BlockchainError(BlockchainErrorCode.ROFL_UNAVAILABLE, "ROFL service URL is not configured")
