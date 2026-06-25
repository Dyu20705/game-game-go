# Blockchain Prephase Audit

Status: technical preparation for Oasis Sapphire/ROFL. Not production-ready and not deployed.

## What Exists

- Foundry contract folder with Game Game Go no-wager contracts.
- Python blockchain domain, ports, local adapters and static Oasis adapter boundaries.
- Local/offline mode remains default and requires no wallet/RPC/ROFL.
- SquareXO deterministic domain and replay verifier.
- ROFL game-service scaffold now exposes typed request/response verification logic.
- Commitment vectors in `test_vectors/result_commitments.json`.

## Scaffold vs Running Code

Running locally:

- Python local identity/match registry/result verifier.
- SquareXO deterministic replay verification.
- ROFL service unit tests by importing the service boundary.
- Contract source static compilation target, if Foundry is available.

Scaffold only:

- Oasis Sapphire RPC adapter.
- ROFL deployment/container registration.
- Contract deployment scripts.
- Wallet signer UX.
- On-chain ruleset registry.
- Production admin/multisig operations.

## Critical Findings

- Previous `MatchRegistry.submitResult` allowed any address to resolve an active match.
- Previous `Achievements.recordAchievement` allowed any address to grant evidence for any player.
- Previous `ResultRegistry` duplicated result storage independent of `MatchRegistry`.

Fixes implemented:

- MatchRegistry owns match lifecycle and result commitment.
- ResultRegistry is now a deprecated write-reverting placeholder.
- Match result writes require verifier role.
- Achievement writes require verifier role.
- Owner-managed verifier grant/revoke events exist.

## High Findings

- No canonical cross-component commitment spec existed.
- ROFL service was only a placeholder and did not verify replay payloads.
- SquareXO verifier did not reject mismatched claimed result if the final state hash matched.
- Oasis config names were inconsistent and oasis mode did not fail fast on missing config.

Fixes implemented:

- Added `docs/RESULT_COMMITMENT_SPEC.md`.
- Added shared Python commitment helper.
- Added test vector.
- Added typed ROFL verifier boundary and SquareXO plugin.
- Added result mismatch rejection.
- Added `BLOCKCHAIN_MODE`, `OASIS_RPC_URL`, `OASIS_CHAIN_ID`, `MATCH_REGISTRY_ADDRESS`, `ROFL_SERVICE_URL`, timeout and confirmation config.

## Medium Findings

- Foundry tests were placeholders.
- CI workflows were absent.
- Local adapter accepted duplicate result overwrite.
- Local verifier registry accepted duplicate game keys.

Fixes implemented:

- Added self-contained Solidity tests without `forge-std`.
- Added CI workflow for Python, ROFL, Solidity, secret scan and non-blocking dependency audit.
- Local adapter rejects duplicate finalization.
- Verifier registry rejects duplicate keys.

## Trust Model

The chosen model is game-first, off-chain-first, on-chain commitment only.

- Player/client can play locally without wallet.
- Local game output is not authoritative for on-chain settlement.
- ROFL verifier recomputes deterministic replay result and produces a commitment.
- Authorized verifier submits final result commitment to MatchRegistry.
- Contract owner/admin manages verifier authorization.
- Sapphire stores lifecycle/result commitments and events, not realtime gameplay.

## Operation Authorization

| Operation | Caller | Trusted data | Must verify | Replay/idempotency |
| --- | --- | --- | --- | --- |
| Create match | Player/orchestrator | game id, ruleset, participants hash | nonzero ids, unique match id | duplicate match id rejected |
| Activate match | creator or owner | existing created match | lifecycle and caller | active cannot return to created |
| Cancel match | creator or owner | match lifecycle | caller and non-final state | resolved/cancelled final |
| Submit result | verifier role | result commitment | active match, nonzero commitment, verifier role | first result finalizes |
| Record achievement | verifier role | evidence hash | player/id/hash nonzero, verifier role | duplicate player+achievement rejected |
| ROFL verify | service request | replay evidence | schema, game/ruleset, deterministic replay, claimed outcome | idempotency key caches response |

## Attack Surface

- Malicious local clients forging replays or claimed winners.
- Replay from another match/game/ruleset.
- Duplicate submissions.
- Oversized ROFL payloads.
- Compromised verifier role.
- Admin key compromise.
- RPC/ROFL unavailability.
- Stale ruleset versions.
- Log leakage of replay payloads.

See `docs/THREAT_MODEL.md` for likelihood, impact and residual risk.

## Gaps Before Oasis Testnet

- Pin Foundry version and run `forge test` in CI.
- Deploy MatchRegistry and Achievements to Sapphire testnet.
- Store deployed addresses in a versioned registry.
- Implement Oasis transaction adapter with checksum address validation.
- Implement ROFL HTTP client against typed request/response schema.
- Build and register ROFL bundle.
- Decide ABI/Keccak commitment encoding or explicitly keep SHA-256 commitments as verifier-supplied bytes32.
- Add integration tests with mocked RPC/ROFL and then live testnet smoke tests.
- Define verifier key custody and rotation runbook.

## Gaps Before Production

- External contract/security review.
- Multisig/timelock or equivalent owner controls.
- Incident response and verifier revocation runbook.
- Reorg/confirmation policy validated against Sapphire.
- Dependency lock/audit policy.
- Observability without replay payload leakage.
- Privacy review for any confidential replay/state.
- Load/DoS testing for ROFL payload limits and idempotency store.
