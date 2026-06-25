# Game Game Go ROFL Verifier

MVP scope:

- verify versioned SquareXO replays;
- reject unknown games/rulesets;
- return deterministic result commitments;
- reject malformed, oversized and mismatched claimed-result payloads;
- cache repeated idempotency keys;
- no wallet seed management;
- no wagering or payout logic.

Validation status in this repository: unit-tested Python service boundary. This
folder has not been built as a ROFL bundle or deployed to testnet in the current
environment.
