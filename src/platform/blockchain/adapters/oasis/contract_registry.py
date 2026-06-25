"""Contract address registry."""


class ContractRegistry:
    def __init__(self, addresses: dict[str, str] | None = None):
        self.addresses = dict(addresses or {})

    def get(self, name: str) -> str | None:
        return self.addresses.get(name)
