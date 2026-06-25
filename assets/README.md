# Assets

`assets/` is the canonical asset root for Game Game Go.

```text
assets/
  brand/       App logo and brand marks.
  platform/    Shared platform UI assets and fallbacks.
  games/       Game-owned thumbnails, covers, icons, and images.
  audio/       Menu/game audio files.
  fonts/       Bundled fonts, if any.
  docs/        Asset provenance and notes.
```

Use `src.platform.services.AssetService` to resolve and load assets. Runtime code should not depend on the current working directory or load from the legacy `asset/` root.

Generated project assets and checksums are maintained by:

```bash
py tools/process_assets.py
```
