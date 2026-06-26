"""Build a lightweight runtime release package for Game Game Go."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

from src.platform.version import APP_NAME, STUDIO_NAME, __version__

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
PACKAGE_SLUG = f"game-game-go-{__version__}-runtime"
STAGING = DIST / PACKAGE_SLUG
ZIP_PATH = DIST / f"{PACKAGE_SLUG}.zip"

RUNTIME_ASSET_DIRS = (
    "audio",
    "backgrounds",
    "branding",
    "docs",
    "fonts",
    "games",
    "platform",
)


def main() -> int:
    from tools.process_assets import main as process_assets

    process_assets()
    _reset_staging()
    _copy_runtime_tree(ROOT / "src", STAGING / "src")
    _copy_runtime_assets()
    _copy_required_files()
    _write_launcher()
    _write_release_readme()
    _write_manifest()
    _zip_staging()
    _write_checksum()
    print(ZIP_PATH)
    return 0


def _reset_staging() -> None:
    DIST.mkdir(exist_ok=True)
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()


def _copy_runtime_tree(source: Path, destination: Path) -> None:
    def ignore(_directory, names):
        return {name for name in names if name in {"__pycache__", ".pytest_cache"} or name.endswith((".pyc", ".pyo"))}

    shutil.copytree(source, destination, ignore=ignore)


def _copy_runtime_assets() -> None:
    assets_destination = STAGING / "assets"
    assets_destination.mkdir()
    for directory in RUNTIME_ASSET_DIRS:
        source = ROOT / "assets" / directory
        if source.exists():
            _copy_runtime_tree(source, assets_destination / directory)
    for filename in ("branding_manifest.json",):
        source = ROOT / "assets" / filename
        if source.exists():
            shutil.copy2(source, assets_destination / filename)


def _copy_required_files() -> None:
    for filename in ("README.md", "CHANGELOG.md", "requirements.txt", "pyproject.toml"):
        source = ROOT / filename
        if source.exists():
            shutil.copy2(source, STAGING / filename)
    license_path = ROOT / "LICENSE"
    if license_path.exists():
        shutil.copy2(license_path, STAGING / "LICENSE")
    third_party = ROOT / "docs" / "THIRD_PARTY_LICENSES.md"
    if third_party.exists():
        docs = STAGING / "docs"
        docs.mkdir(exist_ok=True)
        shutil.copy2(third_party, docs / "THIRD_PARTY_LICENSES.md")


def _write_launcher() -> None:
    launcher = """@echo off
setlocal
cd /d "%~dp0"
python -m src.main
"""
    (STAGING / "run_game_game_go.bat").write_text(launcher, encoding="utf-8")


def _write_release_readme() -> None:
    content = f"""# {APP_NAME} {__version__}

Studio: {STUDIO_NAME}

This is a lightweight Windows/Python runtime package, not a PyInstaller exe.

## Requirements

- Windows 10/11 x64 or another desktop OS with Python 3.10+
- Python available as `python`

## Run

```bat
python -m pip install -r requirements.txt
run_game_game_go.bat
```

The app stores settings in the user's `.game_game_go` settings file and does not
require network access for local play.
"""
    (STAGING / "README_RELEASE.md").write_text(content, encoding="utf-8")


def _write_manifest() -> None:
    files = []
    for path in sorted(STAGING.rglob("*")):
        if not path.is_file():
            continue
        files.append(
            {
                "path": path.relative_to(STAGING).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    manifest = {
        "product": APP_NAME,
        "studio": STUDIO_NAME,
        "version": __version__,
        "package": ZIP_PATH.name,
        "files": files,
    }
    (STAGING / "RELEASE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _zip_staging() -> None:
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(STAGING.rglob("*")):
            if path.is_file():
                archive.write(path, PACKAGE_SLUG + "/" + path.relative_to(STAGING).as_posix())


def _write_checksum() -> None:
    checksum = f"{_sha256(ZIP_PATH)}  {ZIP_PATH.name}\n"
    ZIP_PATH.with_suffix(".zip.sha256").write_text(checksum, encoding="utf-8")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
