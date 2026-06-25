# Threat Model

Status: pre-Oasis-testnet technical baseline. This is not a production security sign-off.

## Actors

- Player/client: runs the desktop app.
- Local game: deterministic or interactive game package running inside Game Game Go.
- Future orchestrator/backend: may coordinate matches or relay verifier requests.
- ROFL verifier: deterministic replay verifier in a TEE.
- Contract owner/admin: manages verifier roles and future address rotation.
- Authorized result submitter: account or service allowed to submit verified results.
- Oasis Sapphire runtime: confidential EVM execution environment.
- Malicious client: modifies local code, submits forged replay/result, or spams requests.
- Compromised verifier: has verifier role but submits false commitments.
- Replay attacker: resubmits a valid result in the wrong context.

## Threats

| Threat | Likelihood | Impact | Current mitigation | Residual risk | Phase |
| --- | --- | --- | --- | --- | --- |
| Malicious local client forges result | High | High | Results require deterministic verifier acceptance before verifier-role contract write | Local-only results are still client-trusted unless submitted through verifier | Testnet |
| Replay across game/match/ruleset | Medium | High | Commitment includes domain, game id, ruleset version, match id, participants hash, replay hash, outcome hash and nonce | Current Solidity does not recompute commitment | Testnet |
| Duplicate result submission | Medium | Medium | MatchRegistry finalizes on first result; local adapter rejects duplicate finalized result | Reorg/idempotency not live-tested | Testnet |
| Achievement self-grant | High | Medium | Achievement contract now requires verifier role | Achievement proof semantics still minimal | Testnet |
| Compromised verifier role | Medium | High | Owner can revoke verifier; events record role changes | No multisig/timelock yet | Production |
| Admin key compromise | Medium | High | Explicit owner role, no hidden deployer hard-code | No multisig, rotation runbook incomplete | Production |
| RPC spoof/failure | Medium | Medium | Oasis mode fail-fast on missing config; local mode isolated | Live RPC validation not implemented | Testnet |
| Chain reorg | Low on Sapphire, nonzero | Medium | Confirmation count config exists | No adapter confirmation policy yet | Testnet |
| Stale ruleset version | Medium | Medium | Verifier registry keys by game id + ruleset version | Ruleset registry not on-chain yet | Testnet |
| Cross-game collision | Low | High | Commitment domain and game id | SHA-256 scaffold must be revisited if Solidity computes Keccak later | Testnet |
| Oversized replay denial of service | Medium | Medium | ROFL service payload byte limit | No streaming/chunking policy yet | Testnet |
| Verifier nondeterminism | Medium | High | Plugin protocol requires pure deterministic verification; tests cover SquareXO vector | No sandbox enforcement beyond review/tests | Testnet |
| Log leakage | Medium | High | ROFL service only returns metadata and avoids replay logging | No centralized logging implementation yet | Testnet |
| Dependency/supply-chain risk | Medium | Medium | CI dependency audit job is non-blocking; minimal Solidity dependencies | No lockfile for all tooling yet | Production |

## Current Trust Assumptions

- Local/offline mode is for playability and development, not authoritative settlement.
- Only ROFL/authorized verifier output should become on-chain result commitment.
- Contract owner is trusted to manage verifier roles until multisig governance is introduced.
- SquareXO replay verification is deterministic and independent of Pygame/UI/network/time.

## Open Risks Before Production

- No live Oasis adapter or signer flow has been exercised.
- No ROFL bundle has been built or registered.
- No multisig/timelock/admin recovery design.
- Solidity/Python/ROFL commitment hashing uses a pre-testnet SHA-256 scaffold rather than pinned ABI/Keccak vectors.
- No external audit.
