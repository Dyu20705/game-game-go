"""Identity port."""

from typing import Protocol

from src.platform.blockchain.domain.identity import PlatformIdentity, SignatureResult


class IdentityPort(Protocol):
    def current_identity(self) -> PlatformIdentity | None:
        ...

    def sign_challenge(self, challenge: bytes) -> SignatureResult:
        ...

