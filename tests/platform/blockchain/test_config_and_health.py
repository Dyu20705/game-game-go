from src.platform.blockchain.adapters.local import LocalIdentity, LocalMatchRegistry, LocalResultVerifier
from src.platform.blockchain.config import BlockchainMode, OasisNetworkConfig
from src.platform.blockchain.domain.network import ChainHealthStatus
from src.platform.blockchain.services.blockchain_service import BlockchainService


def test_offline_health_is_not_configured():
    service = BlockchainService(OasisNetworkConfig(), LocalIdentity(), LocalMatchRegistry(), LocalResultVerifier())

    health = service.health()

    assert health.mode == "offline"
    assert health.sapphire == ChainHealthStatus.NOT_CONFIGURED


def test_local_health_is_connected_without_network():
    service = BlockchainService(
        OasisNetworkConfig(mode=BlockchainMode.LOCAL, network_name="local"),
        LocalIdentity(),
        LocalMatchRegistry(),
        LocalResultVerifier(),
    )

    health = service.health()

    assert health.sapphire == ChainHealthStatus.CONNECTED
    assert health.rofl == ChainHealthStatus.CONNECTED

