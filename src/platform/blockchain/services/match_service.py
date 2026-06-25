"""Match use cases built on registry/verifier ports."""

from src.platform.blockchain.domain.match import CreateMatchRequest


class MatchService:
    def __init__(self, registry):
        self.registry = registry

    def create_match(self, request: CreateMatchRequest):
        return self.registry.create_match(request)
