# Docker Demo

Game Game Go is a desktop Pygame application. The Docker setup is for
repeatable tests, headless smoke checks and optional local visual review through
noVNC. It is not a production web deployment.

## Profiles

```bash
docker compose --profile test run --rm test
docker compose --profile smoke run --rm smoke
docker compose --profile demo up demo
```

The demo binds noVNC to `127.0.0.1:6080` by default. Open
`http://127.0.0.1:6080/vnc.html` locally after the service starts.

Do not expose the demo profile on a public interface. It has no authentication
and is intended only for local review.
