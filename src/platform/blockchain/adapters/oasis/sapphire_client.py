"""Placeholder Sapphire adapter boundary.

The MVP keeps live Oasis calls disabled unless a dedicated integration supplies
an implementation. Gameplay should use local adapters by default.
"""

from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


class SapphireClient:
    def __init__(self, config):
        self.config = config

    def require_configured(self):
        if not self.config.rpc_endpoint:
            raise BlockchainError(BlockchainErrorCode.CONTRACT_NOT_CONFIGURED, "Sapphire RPC is not configured")

