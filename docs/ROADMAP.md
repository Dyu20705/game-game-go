# Roadmap

Near-term:

- Move legacy Color Wars tests to `tests/games/color_wars` and import the new namespace.
- Remove old compatibility modules after migration confidence is high.
- Expand SquareXO conformance vectors by running a generator against the source TypeScript package.
- Implement non-blocking background job handling for testnet RPC/ROFL requests.
- Run and pin Foundry tests in CI with a fixed toolchain version.
- Build/register the ROFL verifier bundle and add mocked RPC/ROFL integration tests.
- Decide ABI/Keccak commitment encoding or explicitly keep SHA-256 commitments as verifier-supplied bytes32.
- Add verifier key custody, rotation and revocation runbooks.
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
