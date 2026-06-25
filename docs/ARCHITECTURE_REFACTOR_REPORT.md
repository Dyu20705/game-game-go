# Architecture Refactor Report

## Before / After Tree

Before this pass, Color Wars still had duplicate root modules:

```text
src/
  ai/
  engine/
  game/
  view/
  controller.py
  games/color_wars/
  platform/
```

After this pass:

```text
src/
  main.py
  games/
    color_wars/
    demo_game/
    nuts_and_bolts/
    square_xo/
  platform/
    bootstrap/
    blockchain/
    games/
    scenes/
    services/
    ui/
```

## Dependency Violations Removed

- Legacy root import count is now `0`.
- Duplicate root Color Wars modules are removed.
- Platform runtime no longer imports SquareXO verifier internals.
- `src.platform.bootstrap` is the composition root allowed to import public game adapters.
- Architecture tests enforce no platform-to-game-internals imports, no game-to-game imports, no domain-to-Pygame imports and no source package cycles.

See `docs/SRC_DEPENDENCY_AUDIT.md` for the generated import graph and current package audit.

## Public API

The public game integration API remains:

- `GameDescriptor`
- `GameModule`
- `GameSession`
- `GameLaunchOptions`
- `GameExitResult`
- `GameExitAction`
- `GameCapability`
- `GameRegistry`
- `DuplicateGameError`
- `GameNotFoundError`

Games are registered via public adapters such as `src.games.color_wars.game.ColorWarsGame`.

## Legacy Files Removed

- `src/controller.py`
- `src/ai/`
- `src/engine/`
- `src/game/`
- `src/view/`

Tests were migrated to import `src.games.color_wars.*` directly instead of keeping compatibility wrappers.

## Classes / Functions Split

- `src.platform.bootstrap.composition.build_default_registry()` now owns static game registration.
- `src.platform.bootstrap.composition.build_platform_context()` now owns service and adapter wiring.
- `PlatformApp` now focuses on scene flow and game launch orchestration.
- `SquareXOGame.register_verifiers()` exposes verifier registration through the public game adapter.

## Architecture Tests

Added `tests/architecture/test_import_boundaries.py` for:

- removed legacy root modules;
- no legacy root imports;
- no platform imports of game internals outside bootstrap;
- no game-to-game imports;
- no domain imports of Pygame;
- no source package cycles;
- explicit `src.platform.games` public API.

## Test Commands / Results

- `py -m pytest -q -p no:cacheprovider`: 157 passed.
- `py -m compileall src tests tools rofl\game-service\src rofl\game-service\tests`: passed.
- `py -m ruff check src tests tools rofl\game-service\src rofl\game-service\tests`: passed.
- `py -m ruff format --check src tests tools rofl\game-service\src rofl\game-service\tests`: passed.

Foundry was not run locally because `forge` is not installed in this environment.

## Remaining Technical Debt

- P1: Split large presentation modules such as `src.platform.scenes.library_scene` and Color Wars home/gameplay scene helpers.
- P1: Add mocked RPC/ROFL integration tests before live Oasis testnet work.
- P2: Move old `tests/ai`, `tests/game`, `tests/game_logic` and `tests/view` files under `tests/games/color_wars` once the team is ready for test tree cleanup.
- P2: Continue extracting Color Wars runtime text into localization keys.
- P3: Consider package-local Color Wars asset data after current canonical `assets/` root settles.
