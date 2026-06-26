# Testing Guide

Primary commands:

```bash
python -m ruff check src tests tools rofl/game-service/src rofl/game-service/tests
python -m ruff format --check src tests tools rofl/game-service/src rofl/game-service/tests
python -m compileall src tests tools rofl/game-service/src rofl/game-service/tests
python -m pytest -q -p no:cacheprovider
python -m pytest --cov --cov-report=term-missing --cov-report=xml -q -p no:cacheprovider
python -m tools.smoke_test
python -m tools.check_links
```

Pygame tests run headlessly through SDL dummy settings in the test fixtures and
smoke command.
