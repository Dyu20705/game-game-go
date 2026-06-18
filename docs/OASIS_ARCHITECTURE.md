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

## Oasis Adapters

Current status: `STATIC_VALIDATION`.

Typed adapter boundaries exist for Sapphire, ROFL, contract address lookup and
transaction error mapping. Live RPC calls, signer flows, ROFL bundle builds and
testnet deployment are not claimed in the current validation.

