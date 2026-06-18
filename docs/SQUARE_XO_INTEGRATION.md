# SquareXO Integration

Source repository audited:

```text
https://github.com/VuNgNgocBao04/SQUAREXO.git
revision: fffd7c2030443e60e90572277f2968f70acbf21d
license: Apache-2.0
```

Windows clone warning: the source has a case-sensitive path collision between
`GameCanvas.tsx` and `gameCanvas.tsx`. Integration avoids copying the frontend
verbatim.

## Source Findings

SquareXO is a TypeScript monorepo:

- `packages/game-core`: deterministic Dots & Boxes style rules.
- `packages/frontend`: React/Vite canvas UI.
- `packages/backend`: Socket.IO rooms, users, history, blockchain service.
- `packages/contracts`: Hardhat Solidity contract for Oasis Sapphire.

The reusable gameplay core is small:

- `createGame(rows, cols)` creates horizontal and vertical edges.
- `applyMove(state, edge)` claims the current player's edge.
- direction-insensitive edge keys are used.
- completing one or more squares scores and keeps the turn.
- invalid or duplicate edges throw.

## Ported Modules

Ported into Python:

```text
src/games/square_xo/domain/
  board.py
  move.py
  replay.py
  result.py
  rules.py
  state.py
```

The Python port preserves source semantics and adds terminal helpers, canonical
serialization and SHA-256 hashes for platform verification.

## Wagering Safeguards

The source contract includes native-value betting fields and payout functions:

- `betAmount`;
- `totalPot`;
- payable create/join functions;
- `claimReward`;
- refund/payout transfers.

These are not integrated into Game Game Go user flow. Game Game Go SquareXO
uses `stake_mode = NO_STAKE` and defaults to `blockchain_mode = LOCAL_MOCK`.

No deposit, withdrawal, fee, payout, token, mainnet wager, or automatic signing
is implemented.

## Active Modes

- `local_1v1`: playable offline/local Pygame session.

Reserved but disabled:

- online friend match;
- P2P transport;
- Oasis testnet submission.

