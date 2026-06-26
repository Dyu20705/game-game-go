# Docker Demo

Game Game Go is a desktop Pygame app. Docker is used here for repeatable tests,
headless smoke checks and an optional local noVNC demo. It is not a production
web service deployment.

## Commands

```bash
docker build .
docker compose --profile test run --rm test
docker compose --profile smoke run --rm smoke
docker compose --profile demo up demo
```

The demo profile binds noVNC to `127.0.0.1:6080`. Open
`http://127.0.0.1:6080/vnc.html` locally. Do not expose this profile publicly.

The image runs as a non-root user and defaults to `python -m tools.smoke_test`.
It does not run a blockchain node and does not claim production readiness.

## GitHub Social Preview

GitHub repository settings do not automatically read social preview images from
the repository. To use the committed preview, upload
`assets/branding/github_social_preview.png` in the repository's social preview
settings.
