from src.platform.blockchain.adapters.local import LocalIdentity, LocalMatchRegistry, LocalResultVerifier
from src.platform.blockchain.adapters.oasis.network_config import is_oasis_configured
from src.platform.blockchain.adapters.oasis.rofl_client import RoflClient
from src.platform.blockchain.config import BlockchainMode, OasisNetworkConfig
from src.platform.blockchain.domain.network import ChainHealthStatus
from src.platform.blockchain.errors import BlockchainError, BlockchainErrorCode
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


def test_oasis_mode_fails_fast_when_required_env_missing(monkeypatch):
    monkeypatch.setenv("BLOCKCHAIN_MODE", "oasis_testnet")
    monkeypatch.delenv("OASIS_RPC_URL", raising=False)
    monkeypatch.delenv("OASIS_CHAIN_ID", raising=False)
    monkeypatch.delenv("MATCH_REGISTRY_ADDRESS", raising=False)
    monkeypatch.delenv("ROFL_SERVICE_URL", raising=False)

    try:
        OasisNetworkConfig.from_environment()
    except BlockchainError as exc:
        assert exc.code == BlockchainErrorCode.CONTRACT_NOT_CONFIGURED
        assert "OASIS_RPC_URL" in str(exc)
    else:
        raise AssertionError("missing oasis config was accepted")


def test_oasis_mode_accepts_standard_env_names(monkeypatch):
    monkeypatch.setenv("BLOCKCHAIN_MODE", "oasis_testnet")
    monkeypatch.setenv("OASIS_RPC_URL", "https://testnet.example")
    monkeypatch.setenv("OASIS_CHAIN_ID", "23295")
    monkeypatch.setenv("MATCH_REGISTRY_ADDRESS", "0x0000000000000000000000000000000000000001")
    monkeypatch.setenv("ROFL_SERVICE_URL", "https://rofl.example")

    config = OasisNetworkConfig.from_environment()

    assert config.mode == BlockchainMode.OASIS_TESTNET
    assert config.chain_id == 23295
    assert config.contract_addresses["match_registry"].endswith("0001")
    assert config.rofl_service_url == "https://rofl.example"


def test_oasis_ready_requires_match_registry_and_rofl_service_url():
    config = OasisNetworkConfig(
        mode=BlockchainMode.OASIS_TESTNET,
        chain_id=23295,
        rpc_endpoint="https://testnet.example",
        rofl_app_id="rofl-app-only",
        contract_addresses={"match_registry": "0x0000000000000000000000000000000000000001"},
    )

    assert not is_oasis_configured(config)

    ready_config = OasisNetworkConfig(
        mode=BlockchainMode.OASIS_TESTNET,
        chain_id=23295,
        rpc_endpoint="https://testnet.example",
        rofl_service_url="https://rofl.example",
        contract_addresses={"match_registry": "0x0000000000000000000000000000000000000001"},
    )

    assert is_oasis_configured(ready_config)


def test_rofl_client_requires_service_url_not_app_id_only():
    client = RoflClient(OasisNetworkConfig(rofl_app_id="rofl-app-only"))

    try:
        client.require_configured()
    except BlockchainError as exc:
        assert exc.code == BlockchainErrorCode.ROFL_UNAVAILABLE
        assert "service URL" in str(exc)
    else:
        raise AssertionError("ROFL client accepted app id without service URL")

    RoflClient(OasisNetworkConfig(rofl_service_url="https://rofl.example")).require_configured()
