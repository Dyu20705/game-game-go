"""Blockchain configuration for offline/local/Oasis testnet modes."""

import os
from dataclasses import dataclass, field
from enum import Enum


class BlockchainMode(str, Enum):
    OFFLINE = "offline"
    LOCAL = "local"
    OASIS_TESTNET = "oasis_testnet"


@dataclass(frozen=True)
class OasisNetworkConfig:
    """Typed network configuration with safe defaults."""

    mode: BlockchainMode = BlockchainMode.OFFLINE
    network_name: str = "offline"
    chain_id: int | None = None
    rpc_endpoint: str | None = None
    explorer_base_url: str | None = None
    rofl_app_id: str | None = None
    contract_addresses: dict[str, str] = field(default_factory=dict)
    request_timeout_seconds: float = 8.0

    @classmethod
    def from_environment(cls):
        raw_mode = os.environ.get("GAME_GAME_GO_MODE", "offline").strip().lower()
        mode = BlockchainMode(raw_mode) if raw_mode in {item.value for item in BlockchainMode} else BlockchainMode.OFFLINE
        if mode != BlockchainMode.OASIS_TESTNET:
            return cls(mode=mode, network_name=mode.value)
        return cls(
            mode=mode,
            network_name="oasis_sapphire_testnet",
            chain_id=_int_or_none(os.environ.get("OASIS_SAPPHIRE_CHAIN_ID")),
            rpc_endpoint=os.environ.get("OASIS_SAPPHIRE_RPC_URL"),
            explorer_base_url=os.environ.get("OASIS_SAPPHIRE_EXPLORER_URL"),
            rofl_app_id=os.environ.get("OASIS_ROFL_APP_ID"),
            contract_addresses={
                key.removeprefix("GGG_CONTRACT_").lower(): value
                for key, value in os.environ.items()
                if key.startswith("GGG_CONTRACT_") and value
            },
        )


def _int_or_none(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except ValueError:
        return None

