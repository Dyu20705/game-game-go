# Oasis Architecture

Oasis is a shared platform capability in Game Game Go, not a SquareXO-only
dependency.

## Responsibilities

Sapphire should handle platform-level match registration, ruleset commitments,
participant commitments, final result commitments, duplicate submission
protection and optional achievement evidence.

ROFL should handle deterministic replay verification, result attestation and
future match coordination.

The Pygame client handles rendering, input, local/offline gameplay, replay
recording and UX.

## Local Adapters

Implemented:

- `LocalIdentity`;
- `LocalMatchRegistry`;
- `LocalResultVerifier`;
- `BlockchainService.health()`.

These work without RPC, wallet, Docker, Oasis CLI or network.

## Commitment Boundary

Result commitments are specified in `docs/RESULT_COMMITMENT_SPEC.md` and tested
against `test_vectors/result_commitments.json`. In this pre-testnet phase,
contracts store verifier-supplied `bytes32` commitments; they do not recompute
the commitment on-chain.

## Oasis Adapters

Current status: local adapters, SquareXO replay verification, result
commitments and the Python ROFL service boundary are unit-tested. Live RPC
calls, signer flows, ROFL bundle builds and testnet deployment are not claimed
in the current validation.

Typed adapter boundaries exist for Sapphire, ROFL, contract address lookup and
transaction error mapping.

See `docs/BLOCKCHAIN_PREPHASE_AUDIT.md` and `docs/THREAT_MODEL.md` for trust and
authorization details.
