# Roadmap

Near-term:

- Move legacy Color Wars tests to `tests/games/color_wars` and import the new namespace.
- Remove old compatibility modules after migration confidence is high.
- Expand SquareXO conformance vectors by running a generator against the source TypeScript package.
- Implement non-blocking background job handling for testnet RPC/ROFL requests.
- Add real Foundry tests and CI-gated contract compilation.
- Build ROFL verifier beyond placeholder static validation.
- Add a non-blocking scene stack when more platform UI complexity appears.
- Add package-data asset migration for Color Wars.
- Expand localization into Color Wars tutorial/HUD/settings text.

Product:

- User profiles.
- Achievements.
- Statistics.
- Save slots.
- Controller support.
- Accessibility settings.
- Richer localization and font fallback.
- Distribution/package builds.

Longer-term architecture:

- Optional manifest discovery.
- Game update/versioning metadata.
- Plugin discovery for trusted local packages.
- Visual regression checks for key Pygame screens.
