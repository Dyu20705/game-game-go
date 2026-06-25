"""Blockchain identity domain types."""

from dataclasses import dataclass
from enum import Enum


class IdentityKind(str, Enum):
    GUEST_LOCAL = "guest_local"
    WALLET_READ_ONLY = "wallet_read_only"
    WALLET_CONNECTED_TESTNET = "wallet_connected_testnet"


@dataclass(frozen=True)
class PlatformIdentity:
    identity_id: str
    display_name: str
    kind: IdentityKind = IdentityKind.GUEST_LOCAL
    address: str | None = None


@dataclass(frozen=True)
class SignatureResult:
    identity: PlatformIdentity
    signature: bytes
    algorithm: str
