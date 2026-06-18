"""Chain health port."""

from typing import Protocol

from src.platform.blockchain.domain.network import ChainHealth


class ChainHealthPort(Protocol):
    def health(self) -> ChainHealth:
        ...

