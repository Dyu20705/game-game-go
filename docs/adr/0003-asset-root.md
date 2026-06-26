# ADR 0003: Canonical Asset Root

## Decision

Runtime assets live under the repository-level `assets/` root and are loaded
through the platform asset service.

## Consequences

- README and docs can reference stable runtime brand images in `assets/branding/`,
  while source art stays in `assets/source_branding/`.
- Game thumbnails live under `assets/games/<game_id>/`.
- Future package-data migration should preserve the public asset service
  contract.
