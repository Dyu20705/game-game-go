"""Blockchain configuration for offline/local/Oasis testnet modes."""

import os
from dataclasses import dataclass, field
from enum import Enum

from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode


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
    rofl_service_url: str | None = None
    contract_addresses: dict[str, str] = field(default_factory=dict)
    request_timeout_seconds: float = 8.0
    confirmation_count: int = 1

    @classmethod
    def from_environment(cls):
        raw_mode = os.environ.get("BLOCKCHAIN_MODE", os.environ.get("GAME_GAME_GO_MODE", "offline")).strip().lower()
        mode = (
            BlockchainMode(raw_mode) if raw_mode in {item.value for item in BlockchainMode} else BlockchainMode.OFFLINE
        )
        if mode != BlockchainMode.OASIS_TESTNET:
            return cls(mode=mode, network_name=mode.value)
        config = cls(
            mode=mode,
            network_name="oasis_sapphire_testnet",
            chain_id=_int_or_none(os.environ.get("OASIS_CHAIN_ID") or os.environ.get("OASIS_SAPPHIRE_CHAIN_ID")),
            rpc_endpoint=os.environ.get("OASIS_RPC_URL") or os.environ.get("OASIS_SAPPHIRE_RPC_URL"),
            explorer_base_url=os.environ.get("OASIS_EXPLORER_URL") or os.environ.get("OASIS_SAPPHIRE_EXPLORER_URL"),
            rofl_app_id=os.environ.get("ROFL_APP_ID") or os.environ.get("OASIS_ROFL_APP_ID"),
            rofl_service_url=os.environ.get("ROFL_SERVICE_URL"),
            contract_addresses={
                "match_registry": os.environ.get("MATCH_REGISTRY_ADDRESS")
                or os.environ.get("GGG_CONTRACT_MATCH_REGISTRY", ""),
                "achievement_registry": os.environ.get("ACHIEVEMENT_REGISTRY_ADDRESS")
                or os.environ.get("GGG_CONTRACT_ACHIEVEMENTS", ""),
            },
            request_timeout_seconds=_float_or_default(os.environ.get("REQUEST_TIMEOUT_SECONDS"), 8.0),
            confirmation_count=_int_or_default(os.environ.get("CONFIRMATION_COUNT"), 1),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.mode != BlockchainMode.OASIS_TESTNET:
            return
        missing = []
        if not self.rpc_endpoint:
            missing.append("OASIS_RPC_URL")
        if self.chain_id is None:
            missing.append("OASIS_CHAIN_ID")
        if not self.contract_addresses.get("match_registry"):
            missing.append("MATCH_REGISTRY_ADDRESS")
        if not self.rofl_service_url:
            missing.append("ROFL_SERVICE_URL")
        if missing:
            raise BlockchainError(
                BlockchainErrorCode.CONTRACT_NOT_CONFIGURED,
                f"oasis_testnet mode missing config: {', '.join(missing)}",
            )


def _int_or_none(value: str | None) -> int | None:
    try:
        return int(value) if value else None
    except ValueError:
        return None


def _int_or_default(value: str | None, default: int) -> int:
    parsed = _int_or_none(value)
    return parsed if parsed is not None else default


def _float_or_default(value: str | None, default: float) -> float:
    try:
        return float(value) if value else default
    except ValueError:
        return default
