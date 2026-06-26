# Asset and UX Audit

## Inventory

Legacy `asset/` contained three menu audio tracks, Color Wars images, and unused Hero image sprites. No `assets/` root existed before this pass.

Current canonical root:

```text
assets/
  source_branding/
  branding/
  backgrounds/
  platform/
  games/
    color_wars/
    square_xo/
    nuts_and_bolts/
  audio/
  fonts/
  docs/
```

## Migration Decisions

- Moved audio to `assets/audio/` and renamed files to snake_case.
- Moved Color Wars images to `assets/games/color_wars/images/`.
- Generated project-created brand marks, fallback thumbnail, and 16:9 game card thumbnails with `tools/process_assets.py`.
- Wrote `assets/manifest.json` with byte sizes, SHA-256 checksums, and license/provenance fields.
- Removed the legacy `asset/` root. `AssetService.legacy()` remains only as an in-code compatibility shim that maps old logical paths to `assets/`.

## Orphans

The old `asset/img/Hero/*` sprites had no references in `src/`, `tests/`, docs, or manifests, and no registered `the_heroic_cube` game implementation was present. They were not migrated.

## Hard-Coded Paths Fixed

- Platform boot audio now uses `AssetService.audio("")`.
- The stale PyInstaller spec was removed because it still built a Color Wars-named app.
  Future desktop packaging must use the Game Game Go name and bundle `assets/`.
- Color Wars compatibility audio/window/home-scene helpers now resolve from `assets/`.
- Game manifests now declare thumbnails.
- Library cards load thumbnails through `AssetService` instead of importing game internals or drawing game-specific fake art.

## Runtime and Cache

`AssetService` now provides:

- brand, platform, game, and audio namespace resolvers;
- original image cache;
- scaled image cache keyed by path, size, and scale mode;
- font cache keyed by font id, size, bold, and italic;
- bounded cache sizes;
- placeholder image fallback for missing or broken assets;
- safe font fallback for missing bundled fonts or headless tests.

## UX Issues Addressed

- Home uses the brand mark and cached fonts.
- Library cards use consistent 16:9 thumbnails and retain keyboard/mouse launch behavior.
- Shared platform theme gained semantic colors, focus color, motion timings, target sizes, and breakpoints.
- Shared components now support button state, focus ring, pills, status messages, and loading indicator while preserving the old `draw_button` API.

## Remaining Limits

- Several legacy Color Wars gameplay modules still create fonts inside draw paths. They are outside the platform shell polish path and should be handled in a gameplay-specific performance pass.
- Platform settings and secondary scenes still use simple blocking scene loops. They share `context.clock` and lifecycle correctly, but are not yet a full retained UI system.
- Audio provenance for third-party tracks is recorded in `assets/manifest.json`; redistribution licensing should be confirmed before public release.
