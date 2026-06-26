# Assets

`assets/` is the canonical asset root for Game Game Go.

```text
assets/
  source_branding/  Original supplied studio, product logo, and vertical background art.
  branding/         Optimized runtime logos, icons, social preview, and hero art.
  backgrounds/      Runtime PC menu backgrounds and previews.
  platform/    Shared platform UI assets and fallbacks.
  games/       Game-owned thumbnails, covers, icons, and images.
  audio/       Menu/game audio files.
  fonts/       Bundled fonts, if any.
  docs/        Asset provenance and notes.
```

Use `src.platform.services.AssetService` to resolve and load assets. Runtime code should not depend on the current working directory or load from the legacy `asset/` root.

Branding derivatives are maintained by:

```bash
py -m tools.prepare_branding_assets
```

All generated project assets and checksums are maintained by:

```bash
py -m tools.process_assets
```
