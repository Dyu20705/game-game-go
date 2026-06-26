# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    SDL_VIDEODRIVER=dummy \
    SDL_AUDIODRIVER=dummy \
    BLOCKCHAIN_MODE=local

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libsdl2-2.0-0 \
        novnc \
        supervisor \
        websockify \
        x11vnc \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt pytest pytest-cov ruff

COPY assets ./assets
COPY rofl ./rofl
COPY src ./src
COPY tests ./tests
COPY test_vectors ./test_vectors
COPY tools ./tools
COPY docker ./docker

RUN chmod +x /app/docker/entrypoint.sh \
    && useradd --create-home --shell /bin/sh appuser \
    && chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -m tools.smoke_test

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["smoke"]
