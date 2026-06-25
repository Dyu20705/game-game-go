"""Oasis network config helpers."""

from src.platform.blockchain.config import OasisNetworkConfig


def is_oasis_configured(config: OasisNetworkConfig) -> bool:
    return bool(
        config.rpc_endpoint
        and config.chain_id
        and config.contract_addresses.get("match_registry")
        and config.rofl_service_url
    )
