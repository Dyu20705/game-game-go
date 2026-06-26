# Color Wars

Color Wars is the original strategy game module. It now lives entirely under
`src/games/color_wars`.

## Ownership

- Rules and explosion logic: `engine/`
- AI strategies: `ai/`
- Runtime/session state: `runtime/`
- Pygame presentation: `view/`
- Platform adapter: `game.py`

## Current Modes

- PvP local.
- PvBot local with easy, medium and hard AI.

There is no wallet, token, payout or network dependency in Color Wars.
