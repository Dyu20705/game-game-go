# Test Audit

Status after hardening: `py -m pytest -q -p no:cacheprovider` passes with 157
tests in this environment.

Coverage baseline from the hardening run is 42% total branch coverage. No
coverage badge is published because there is no external coverage service wired
for a durable badge yet.

## Inventory

| Area | Current Location | Notes |
| --- | --- | --- |
| Platform unit/integration | `tests/platform/` | Registry, descriptors, save/settings, scenes, assets |
| Blockchain/local adapters | `tests/platform/blockchain/` | Local identity, registry, verifier, config, commitment vectors |
| Color Wars legacy-domain tests | `tests/ai`, `tests/game`, `tests/game_logic`, `tests/view` | Imports migrated to `src.games.color_wars.*`; physical move deferred to avoid noisy history churn |
| Game contract tests | `tests/games/*` | Game descriptors, lifecycle/session contracts |
| SquareXO domain/replay | `tests/games/square_xo/`, `tests/conformance/` | Deterministic rules, conformance vectors, replay verifier |
| ROFL boundary | `rofl/game-service/tests/` | Service schema, idempotency, payload limits |
| Architecture | `tests/architecture/` | AST import-boundary tests |

## Findings

- Legacy root imports: none.
- Skipped tests: none in the default suite.
- Network dependency: none in default tests.
- Pygame tests: run headlessly with SDL dummy fixtures.
- Screenshot/golden tests: none.
- Slow tests: none identified in the local suite.
- Duplicate coverage: some Color Wars tests remain in old physical folders, but
  they assert current game-package imports and are kept rather than deleted.
- Brittle mocks: a few Color Wars rendering tests patch draw helpers; retained
  because they protect transitional blocking UI behavior.

## Markers

`pytest.ini` defines optional markers:

- `unit`
- `integration`
- `architecture`
- `pygame`
- `blockchain`
- `rofl`
- `smoke`

The suite is still mostly domain-folder-based; markers are available for future
selection without forcing a large test move in this hardening pass.

## Recommended Next Cleanup

Move `tests/ai`, `tests/game`, `tests/game_logic` and `tests/view` under
`tests/unit/games/color_wars` or `tests/games/color_wars` in a dedicated
test-layout-only change.
