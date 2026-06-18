# SquareXO Conformance

The integrated Python implementation is based on the audited TypeScript
`packages/game-core` source at revision `fffd7c2030443e60e90572277f2968f70acbf21d`.

## Source Semantics

- players are `X` and `O`;
- initial player is `X`;
- generated edges count is `(rows + 1) * cols + rows * (cols + 1)`;
- edge matching is direction-independent;
- claiming an already taken edge is invalid;
- invalid diagonal/off-board edge is invalid;
- completing a square increments current player's score;
- completing a square keeps the current player turn.

## Vectors

Vectors are stored in:

```text
tests/conformance/square_xo_vectors/basic_vectors.json
```

The Python integration adds explicit terminal/result helpers and canonical
hashing because the source core leaves terminal status inferred. This is an
extension for platform lifecycle and verification, not a gameplay rule change.

