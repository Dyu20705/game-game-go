# Testing

## Test Groups

```text
tests/platform/              Platform registry, descriptor, settings, save, assets, scene action.
tests/games/color_wars/      Color Wars contract and launch option adapter tests.
tests/games/demo_game/       Demo game contract/lifecycle tests.
tests/games/square_xo/       SquareXO domain, conformance, replay and contract tests.
tests/games/nuts_and_bolts/  Nuts & Bolts manifest, domain, session lifecycle and registry tests.
tests/platform/blockchain/   Local blockchain adapter/config/health/commitment tests.
rofl/game-service/tests/     ROFL verifier service boundary tests.
contracts/test/              Foundry contract authorization/lifecycle tests.
tests/architecture/          AST dependency boundary tests.
tests/game_logic/            Legacy Color Wars rules/controller/explosion tests.
tests/ai/                    Legacy Color Wars AI tests.
tests/game/, tests/view/     Runtime/view tests that require pygame.
```

## Commands Used During Migration

```bash
py -m pytest tests\platform tests\games -q -p no:cacheprovider
py -m pytest tests\game_logic tests\ai -q -p no:cacheprovider
py -m pytest tests\platform tests\games tests\game_logic tests\ai -q -p no:cacheprovider
py -m pytest tests\platform\blockchain tests\games\square_xo rofl\game-service\tests -q -p no:cacheprovider
py -m pytest tests\architecture -q -p no:cacheprovider
py -m compileall -q src tests tools rofl\game-service\src rofl\game-service\tests
py -m ruff check src tests tools rofl\game-service\src rofl\game-service\tests
py -m ruff format --check src tests tools rofl\game-service\src rofl\game-service\tests
```

Results in the current environment:

- Platform/game contract tests: 22 passed.
- Legacy Color Wars logic/AI tests: 18 passed.
- Combined non-Pygame subset: 40 passed.
- SquareXO/Oasis expanded non-Pygame subset: 55 passed.
- Blockchain/ROFL/SquareXO focused subset: 30 passed.
- Architecture boundary tests: 7 passed.
- Full `py -m pytest -q -p no:cacheprovider`: 157 passed.
- Coverage baseline: 42% total branch coverage from `py -m pytest --cov --cov-report=term-missing --cov-report=xml -q -p no:cacheprovider`.
- Compileall: passed.
- Ruff check: passed.
- Ruff format check: passed.
- Two `pytest-cache-files-*` temp directories created during a sandboxed pytest run could not be removed by Windows; `pytest.ini` excludes that pattern from collection.

## Headless Notes

For CI or local headless runs with Pygame installed, use:

```bash
set SDL_VIDEODRIVER=dummy
set SDL_AUDIODRIVER=dummy
pytest -q
```

The repository includes `tests/conftest.py` to keep temporary files inside the workspace when sandboxed environments block the default system temp directory.
