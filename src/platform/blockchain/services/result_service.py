"""Result submission use cases."""

from src.platform.blockchain.domain.result import ReplayVerificationRequest


class ResultService:
    def __init__(self, registry, verifier):
        self.registry = registry
        self.verifier = verifier

    def verify_and_submit(self, envelope):
        verification = self.verifier.verify_replay(ReplayVerificationRequest(envelope))
        if not verification.accepted:
            return verification, None
        return verification, self.registry.submit_result(envelope)

