"""Local anonymous identity adapter."""

from src.platform.blockchain.domain.identity import IdentityKind, PlatformIdentity, SignatureResult


class LocalIdentity:
    def __init__(self, identity_id: str = "guest-local", display_name: str = "Guest"):
        self.identity = PlatformIdentity(identity_id=identity_id, display_name=display_name, kind=IdentityKind.GUEST_LOCAL)

    def current_identity(self) -> PlatformIdentity:
        return self.identity

    def sign_challenge(self, challenge: bytes) -> SignatureResult:
        return SignatureResult(identity=self.identity, signature=b"local:" + challenge, algorithm="local-dev")

