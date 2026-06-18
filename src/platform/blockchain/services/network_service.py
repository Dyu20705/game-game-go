"""Network status service wrapper."""


class NetworkService:
    def __init__(self, blockchain):
        self.blockchain = blockchain

    def status_text(self) -> str:
        health = self.blockchain.health()
        return f"Mode: {health.mode}, Sapphire: {health.sapphire.value}, ROFL: {health.rofl.value}"

