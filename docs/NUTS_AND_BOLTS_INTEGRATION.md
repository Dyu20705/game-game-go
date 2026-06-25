# Nuts & Bolts Integration

## Ownership

Nuts & Bolts lives in `src/games/nuts_and_bolts/`.

- `manifest.py`: public `GameDescriptor`.
- `game.py`: platform adapter exposing `NutsAndBoltsGame`.
- `session.py`: Pygame gameplay session and lifecycle mapping.
- `models.py`, `rules.py`, `level_generator.py`, `animation.py`: game/domain logic.
- `ui/`: Nuts & Bolts-specific drawing helpers.

The stable `game_id` is `nuts_and_bolts`.

## Lifecycle

The game is registered in `build_default_registry()` and launched through `GameRegistry`.
`NutsAndBoltsSession` uses `PlatformContext.screen` and `PlatformContext.clock`; it does not initialize Pygame, create a clock, call `pygame.quit()`, or call `sys.exit()`.

Exit mapping:

- window close returns `GameExitAction.QUIT`;
- Escape returns `GameExitAction.GAME_LIBRARY`;
- the Library button returns `GameExitAction.GAME_LIBRARY`.

The exit payload contains difficulty, move count, and completion status.

## Controls

- Click a non-empty screw to select the top nut.
- Click a destination screw to move the selected nut.
- `Z`: undo.
- `R`: restart current puzzle.
- `Enter`: new puzzle.
- `1`, `2`, `3`: easy, normal, hard.
- `M`: toggle platform sound preference.
- `Esc` or Library button: return to Game Library.

## Difficulty

Valid difficulties are `easy`, `normal`, and `hard`.
Launch options take precedence when valid. Invalid or missing launch options fall back to saved `last_difficulty`, then to `normal`.

## Persisted Stats

The game stores values under `context.settings.get_game_settings("nuts_and_bolts")`:

- `last_difficulty`;
- `total_completed`;
- `best_moves_easy`;
- `best_moves_normal`;
- `best_moves_hard`.

Completion stats are recorded once per puzzle. Best moves only update when the new move count is lower than the saved value.

## Tests

Run:

```bash
python -m pytest -q
python -m compileall src tests
```

For Windows sandbox runs, use:

```bash
py -m pytest -q -p no:cacheprovider
```

## Current Limits

No Nuts & Bolts SFX assets are bundled yet. The local sound adapter is intentionally fail-safe and no-ops for game SFX while still respecting platform sound settings.
