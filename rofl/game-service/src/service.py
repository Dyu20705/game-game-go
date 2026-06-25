"""Deterministic ROFL verifier service boundary for Game Game Go."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any, Protocol

from src.games.square_xo.application.result_submission import verify_square_xo_replay
from src.platform.blockchain.domain.commitment import result_commitment_for_envelope
from src.platform.blockchain.domain.result import (
    CanonicalMatchResult,
    CanonicalMove,
    MatchEnvelope,
    ReplayVerificationRequest,
)


SCHEMA_VERSION = 1
VERIFIER_VERSION = "rofl-verifier-0.1.0"
MAX_PAYLOAD_BYTES = 64 * 1024


@dataclass(frozen=True)
class VerificationResponse:
    schema_version: int
    verifier_version: str
    request_id: str
    idempotency_key: str
    status: str
    accepted: bool
    game_id: str | None = None
    ruleset_version: str | None = None
    match_id: str | None = None
    result_commitment: str | None = None
    reason: str | None = None
    duration_ms: int = 0

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "duration_ms": self.duration_ms,
            "game_id": self.game_id,
            "idempotency_key": self.idempotency_key,
            "match_id": self.match_id,
            "reason": self.reason,
            "request_id": self.request_id,
            "result_commitment": self.result_commitment,
            "ruleset_version": self.ruleset_version,
            "schema_version": self.schema_version,
            "status": self.status,
            "verifier_version": self.verifier_version,
        }


class VerifierPlugin(Protocol):
    def supports(self, game_id: str, ruleset_version: str) -> bool:
        ...

    def verify(self, envelope: MatchEnvelope) -> VerificationResponse:
        ...


class VerifierRegistry:
    def __init__(self) -> None:
        self._plugins: dict[tuple[str, str], VerifierPlugin] = {}

    def register(self, game_id: str, ruleset_version: str, plugin: VerifierPlugin) -> None:
        key = (game_id, ruleset_version)
        if key in self._plugins:
            raise ValueError(f"duplicate verifier plugin: {game_id}/{ruleset_version}")
        self._plugins[key] = plugin

    def get(self, game_id: str, ruleset_version: str) -> VerifierPlugin | None:
        return self._plugins.get((game_id, ruleset_version))

    def supported_rulesets(self) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(self._plugins))


class SquareXOVerifier:
    def __init__(self, ruleset_version: str) -> None:
        self.ruleset_version = ruleset_version

    def supports(self, game_id: str, ruleset_version: str) -> bool:
        return game_id == "square_xo" and ruleset_version == self.ruleset_version

    def verify(self, envelope: MatchEnvelope) -> VerificationResponse:
        result = verify_square_xo_replay(ReplayVerificationRequest(envelope))
        return VerificationResponse(
            schema_version=SCHEMA_VERSION,
            verifier_version=VERIFIER_VERSION,
            request_id="",
            idempotency_key="",
            status="accepted" if result.accepted else "rejected",
            accepted=result.accepted,
            game_id=envelope.game_id,
            ruleset_version=envelope.ruleset_version,
            match_id=envelope.match_id,
            result_commitment=result.result_hash,
            reason=result.reason,
        )


class VerificationService:
    def __init__(self, registry: VerifierRegistry, *, max_payload_bytes: int = MAX_PAYLOAD_BYTES) -> None:
        self.registry = registry
        self.max_payload_bytes = max_payload_bytes
        self._responses_by_idempotency: dict[str, VerificationResponse] = {}

    def verify_json(self, raw_body: bytes | str) -> VerificationResponse:
        started = time.monotonic()
        if isinstance(raw_body, str):
            raw_bytes = raw_body.encode("utf-8")
        else:
            raw_bytes = raw_body
        if len(raw_bytes) > self.max_payload_bytes:
            return self._error("payload_too_large", started=started)
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return self._error("malformed_json", started=started)
        return self.verify(payload, started=started)

    def verify(self, payload: dict[str, Any], *, started: float | None = None) -> VerificationResponse:
        started = started if started is not None else time.monotonic()
        request_id = str(payload.get("request_id") or "")
        idempotency_key = str(payload.get("idempotency_key") or request_id)
        if not request_id or not idempotency_key:
            return self._error("missing_request_id", request_id=request_id, idempotency_key=idempotency_key, started=started)
        if idempotency_key in self._responses_by_idempotency:
            return self._responses_by_idempotency[idempotency_key]
        try:
            envelope = envelope_from_payload(payload)
        except (KeyError, TypeError, ValueError) as exc:
            response = self._error(str(exc) or "schema_error", request_id=request_id, idempotency_key=idempotency_key, started=started)
            self._responses_by_idempotency[idempotency_key] = response
            return response

        plugin = self.registry.get(envelope.game_id, envelope.ruleset_version)
        if plugin is None:
            response = self._error(
                "unsupported_ruleset",
                request_id=request_id,
                idempotency_key=idempotency_key,
                game_id=envelope.game_id,
                ruleset_version=envelope.ruleset_version,
                match_id=envelope.match_id,
                started=started,
            )
            self._responses_by_idempotency[idempotency_key] = response
            return response

        try:
            response = plugin.verify(envelope)
        except Exception:
            response = self._error(
                "verifier_exception",
                request_id=request_id,
                idempotency_key=idempotency_key,
                game_id=envelope.game_id,
                ruleset_version=envelope.ruleset_version,
                match_id=envelope.match_id,
                started=started,
            )
        else:
            result_commitment = (
                result_commitment_for_envelope(
                    envelope,
                    verifier_version=VERIFIER_VERSION,
                    nonce=str(payload.get("nonce") or ""),
                )
                if response.accepted
                else response.result_commitment
            )
            response = VerificationResponse(
                **{
                    **response.to_dict(),
                    "request_id": request_id,
                    "idempotency_key": idempotency_key,
                    "result_commitment": result_commitment,
                    "duration_ms": elapsed_ms(started),
                }
            )
        self._responses_by_idempotency[idempotency_key] = response
        return response

    def _error(
        self,
        reason: str,
        *,
        request_id: str = "",
        idempotency_key: str = "",
        game_id: str | None = None,
        ruleset_version: str | None = None,
        match_id: str | None = None,
        started: float,
    ) -> VerificationResponse:
        return VerificationResponse(
            schema_version=SCHEMA_VERSION,
            verifier_version=VERIFIER_VERSION,
            request_id=request_id,
            idempotency_key=idempotency_key,
            status="rejected",
            accepted=False,
            game_id=game_id,
            ruleset_version=ruleset_version,
            match_id=match_id,
            reason=reason,
            duration_ms=elapsed_ms(started),
        )


def envelope_from_payload(payload: dict[str, Any]) -> MatchEnvelope:
    if int(payload.get("schema_version", 0)) != SCHEMA_VERSION:
        raise ValueError("unsupported_schema_version")
    envelope = payload["envelope"]
    result = envelope["result"]
    return MatchEnvelope(
        protocol_version=str(envelope["protocol_version"]),
        game_id=str(envelope["game_id"]),
        ruleset_version=str(envelope["ruleset_version"]),
        match_id=str(envelope["match_id"]),
        players=tuple(str(player) for player in envelope["players"]),
        initial_state_hash=str(envelope["initial_state_hash"]),
        moves=tuple(CanonicalMove(str(move["move_type"]), dict(move["payload"])) for move in envelope.get("moves", [])),
        final_state_hash=str(envelope["final_state_hash"]),
        result=CanonicalMatchResult(
            winner=result.get("winner"),
            scores={str(key): int(value) for key, value in result.get("scores", {}).items()},
            terminal_reason=str(result["terminal_reason"]),
        ),
        metadata=dict(envelope.get("metadata", {})),
    )


def payload_for_envelope(envelope: MatchEnvelope, *, request_id: str, idempotency_key: str | None = None) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "request_id": request_id,
        "idempotency_key": idempotency_key or request_id,
        "nonce": "",
        "envelope": envelope.to_canonical_dict(),
    }


def default_registry() -> VerifierRegistry:
    from src.games.square_xo.domain.replay import RULESET_VERSION

    registry = VerifierRegistry()
    registry.register("square_xo", RULESET_VERSION, SquareXOVerifier(RULESET_VERSION))
    return registry


def elapsed_ms(started: float) -> int:
    return max(0, int((time.monotonic() - started) * 1000))


def main() -> None:
    registry = default_registry()
    print(
        json.dumps(
            {
                "service": "game-game-go-verifier",
                "schema_version": SCHEMA_VERSION,
                "verifier_version": VERIFIER_VERSION,
                "supported_rulesets": registry.supported_rulesets(),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
