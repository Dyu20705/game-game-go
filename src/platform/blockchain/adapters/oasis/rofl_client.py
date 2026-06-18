"""Placeholder ROFL client boundary."""

from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


class RoflClient:
    def __init__(self, config):
        self.config = config

    def require_configured(self):
        if not self.config.rofl_app_id:
            raise BlockchainError(BlockchainErrorCode.ROFL_UNAVAILABLE, "ROFL app is not configured")

