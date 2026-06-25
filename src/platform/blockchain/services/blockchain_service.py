"""Facade for platform blockchain capabilities."""

from dataclasses import dataclass

from src.platform.blockchain.config import OasisNetworkConfig
from src.platform.blockchain.domain.network import ChainHealth, ChainHealthStatus


@dataclass
class BlockchainService:
    config: OasisNetworkConfig
    identity: object
    match_registry: object
    result_verifier: object

    def health(self) -> ChainHealth:
        if self.config.mode.value == "offline":
            return ChainHealth(
                ChainHealthStatus.NOT_CONFIGURED, ChainHealthStatus.NOT_CONFIGURED, self.config.mode.value
            )
        if self.config.mode.value == "local":
            return ChainHealth(ChainHealthStatus.CONNECTED, ChainHealthStatus.CONNECTED, self.config.mode.value)
        sapphire = ChainHealthStatus.CONNECTED if self.config.rpc_endpoint else ChainHealthStatus.NOT_CONFIGURED
        rofl = (
            ChainHealthStatus.CONNECTED
            if self.config.rofl_service_url or self.config.rofl_app_id
            else ChainHealthStatus.NOT_CONFIGURED
        )
        return ChainHealth(sapphire, rofl, self.config.mode.value)
