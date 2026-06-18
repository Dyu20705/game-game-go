"""Oasis network config helpers."""

from src.platform.blockchain.config import OasisNetworkConfig


def is_oasis_configured(config: OasisNetworkConfig) -> bool:
    return bool(config.rpc_endpoint and config.chain_id)

