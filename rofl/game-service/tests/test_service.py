import importlib.util
import json
import sys
from pathlib import Path


def load_service():
    path = Path("rofl/game-service/src/service.py").resolve()
    spec = importlib.util.spec_from_file_location("rofl_game_service", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def vector_payload():
    service = load_service()
    vector = json.loads(Path("test_vectors/result_commitments.json").read_text(encoding="utf-8"))["vectors"][0]
    return {
        "schema_version": service.SCHEMA_VERSION,
        "request_id": "req-1",
        "idempotency_key": "idem-1",
        "nonce": vector["payload"]["nonce"],
        "envelope": vector["envelope"],
    }


def test_verifies_square_xo_vector_commitment():
    service = load_service()
    verifier = service.VerificationService(service.default_registry())

    response = verifier.verify(vector_payload())

    assert response.accepted is True
    assert response.status == "accepted"
    assert response.result_commitment == "0xa80611bc244f3e89fad4bf2417b4451e991c2fb6404c6bcfb3fbe1e564c3ef4f"


def test_unsupported_game_fails_closed():
    service = load_service()
    payload = vector_payload()
    payload["request_id"] = "req-unsupported"
    payload["idempotency_key"] = "idem-unsupported"
    payload["envelope"]["game_id"] = "color_wars"

    response = service.VerificationService(service.default_registry()).verify(payload)

    assert response.accepted is False
    assert response.reason == "unsupported_ruleset"


def test_mismatched_claimed_result_rejects():
    service = load_service()
    payload = vector_payload()
    payload["request_id"] = "req-mismatch"
    payload["idempotency_key"] = "idem-mismatch"
    payload["envelope"]["result"]["winner"] = "X"

    response = service.VerificationService(service.default_registry()).verify(payload)

    assert response.accepted is False
    assert response.reason == "result_mismatch"


def test_idempotency_returns_first_response():
    service = load_service()
    verifier = service.VerificationService(service.default_registry())
    payload = vector_payload()

    first = verifier.verify(payload)
    payload["envelope"]["result"]["winner"] = "X"
    second = verifier.verify(payload)

    assert first.accepted is True
    assert second is first


def test_malformed_and_oversized_payloads_reject():
    service = load_service()
    verifier = service.VerificationService(service.default_registry(), max_payload_bytes=16)

    malformed = verifier.verify_json("{not json")
    oversized = verifier.verify_json(b"x" * 17)

    assert malformed.accepted is False
    assert malformed.reason == "malformed_json"
    assert oversized.accepted is False
    assert oversized.reason == "payload_too_large"


def test_duplicate_registry_key_rejected():
    service = load_service()
    registry = service.VerifierRegistry()
    plugin = service.SquareXOVerifier("rules")
    registry.register("square_xo", "rules", plugin)

    try:
        registry.register("square_xo", "rules", plugin)
    except ValueError as exc:
        assert "duplicate" in str(exc)
    else:
        raise AssertionError("duplicate verifier was accepted")
