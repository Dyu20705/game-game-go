# Result Commitment Spec

Status: pre-testnet scaffold. This spec is deterministic and unit-tested, but it is not a production attestation format yet.

## Goal

Game Game Go stores commitments to verified results. Realtime gameplay stays off-chain. The commitment binds a replay/result to a game, ruleset, match, participants and verifier version so a result from another context cannot be replayed silently.

## Current Hash Format

The current repository vector format uses canonical JSON plus SHA-256 because the Python and ROFL test environment has no pinned Keccak/ABI encoder dependency. Solidity contracts store a `bytes32 resultCommitment` supplied by an authorized verifier; they do not recompute the hash in this phase.

Future Oasis testnet work may replace the payload encoding with `abi.encode(...)` plus Keccak once the Solidity/Python/ROFL toolchain is pinned and cross-language vectors are regenerated.

## Payload

The canonical payload is sorted JSON with no insignificant whitespace:

```json
{
  "domain": "GGG_RESULT_COMMITMENT_V1",
  "environment": "local",
  "game_id": "square_xo",
  "hash_algorithm": "sha256",
  "match_id": "vector-square-xo-1",
  "nonce": "vector-1",
  "outcome_hash": "0x...",
  "participant_ordering": "ordered",
  "participants_hash": "0x...",
  "replay_hash": "0x...",
  "ruleset_version": "square_xo.port.v1",
  "schema_version": 1,
  "verifier_version": "rofl-verifier-0.1.0"
}
```

`result_commitment = 0x + sha256(canonical_json(payload))`.

## Field Rules

- `schema_version`: integer commitment schema version. Current value: `1`.
- `domain`: fixed domain separator, `GGG_RESULT_COMMITMENT_V1`.
- `environment`: `local`, `offline`, `oasis_testnet`, or future explicit chain environment.
- `game_id`: stable platform game id.
- `ruleset_version`: deterministic rules implementation version.
- `match_id`: registry match id.
- `participants_hash`: hash of participant identifiers.
- `participant_ordering`: `ordered` or `unordered`; SquareXO uses `ordered`.
- `replay_hash`: hash of canonical replay envelope.
- `outcome_hash`: hash of winner, scores, terminal reason and final state hash.
- `nonce`: optional domain nonce/idempotency salt. Empty string is allowed only for local/dev flows.
- `verifier_version`: deterministic verifier implementation version.

## Participant Encoding

Ordered participants:

```json
{"ordering":"ordered","participants":["X","O"]}
```

Unordered participants sort identifiers before hashing.

## Replay Envelope

The replay envelope contains:

- `protocol_version`;
- `game_id`;
- `ruleset_version`;
- `match_id`;
- `players`;
- `initial_state_hash`;
- deterministic moves;
- `final_state_hash`;
- claimed result;
- metadata such as board size.

Verifier implementations must recompute the final state and result from replay evidence. They must reject mismatched final hash or claimed outcome.

## Test Vectors

Committed vectors live in:

```text
test_vectors/result_commitments.json
```

The Python platform and ROFL service tests both verify these vectors.
