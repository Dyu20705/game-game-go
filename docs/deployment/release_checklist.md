# Release Checklist

Game Game Go currently supports a lightweight Python runtime release zip. Use
this checklist before creating a tagged release.

1. Choose a semantic version and tag.
2. Update `CHANGELOG.md`.
3. Run `python -m tools.process_assets` to regenerate optimized branding and checksums.
4. Run lint, format check, compileall, full pytest, coverage, smoke and link check.
5. Build the runtime package with `python -m tools.build_release`.
6. Verify the package name is `game-game-go-<version>-runtime.zip`.
7. Verify `assets/branding/`, `assets/backgrounds/`, game assets and audio are bundled.
8. Verify `assets/source_branding/`, tests, caches and temporary outputs are not bundled.
9. Verify no blockchain deployment claims are added without deployment artifacts.
10. Attach the release zip and `.sha256` checksum manually until a release workflow is intentionally added.
