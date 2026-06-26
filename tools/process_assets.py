"""Validate and generate Game Game Go asset derivatives."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw

from tools.prepare_branding_assets import main as prepare_branding_assets

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
THUMB_SIZE = (640, 360)


def main() -> int:
    ensure_directories()
    prepare_branding_assets()
    create_platform_fallbacks()
    create_game_thumbnails()
    write_manifest()
    return 0


def ensure_directories() -> None:
    for path in (
        ASSETS / "source_branding",
        ASSETS / "branding",
        ASSETS / "backgrounds",
        ASSETS / "platform" / "fallbacks",
        ASSETS / "games" / "color_wars" / "thumbnails",
        ASSETS / "games" / "square_xo" / "thumbnails",
        ASSETS / "games" / "nuts_and_bolts" / "thumbnails",
        ASSETS / "audio",
        ASSETS / "fonts",
        ASSETS / "docs",
    ):
        path.mkdir(parents=True, exist_ok=True)


def create_platform_fallbacks() -> None:
    image = card_base((35, 185, 211), (243, 200, 75))
    draw = ImageDraw.Draw(image)
    draw.ellipse((250, 110, 390, 250), fill=(255, 255, 255, 210))
    draw.ellipse((286, 146, 354, 214), fill=(255, 94, 98, 255))
    save_png(image, ASSETS / "platform" / "fallbacks" / "game_thumbnail.png")


def create_game_thumbnails() -> None:
    create_color_wars_thumbnail()
    create_square_xo_thumbnail()
    create_nuts_and_bolts_thumbnail()


def create_color_wars_thumbnail() -> None:
    image = card_base((255, 94, 98), (35, 185, 211))
    draw = ImageDraw.Draw(image)
    cell = 56
    start_x, start_y = 168, 52
    colors = [(255, 94, 98), (35, 185, 211), (243, 200, 75)]
    for row in range(5):
        for col in range(5):
            x = start_x + col * (cell + 8)
            y = start_y + row * (cell + 8)
            draw.rounded_rectangle((x, y, x + cell, y + cell), radius=12, fill=(247, 249, 251, 230))
            color = colors[(row + col) % len(colors)]
            draw.ellipse((x + 15, y + 15, x + 41, y + 41), fill=color)
    save_png(image, ASSETS / "games" / "color_wars" / "thumbnails" / "card.png")


def create_square_xo_thumbnail() -> None:
    image = card_base((74, 108, 255), (70, 187, 104))
    draw = ImageDraw.Draw(image)
    left, top = 190, 62
    gap = 68
    for row in range(4):
        for col in range(4):
            x = left + col * gap
            y = top + row * gap
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(247, 249, 251))
    for index in range(4):
        y = top + index * gap
        draw.line((left, y, left + gap * 3, y), fill=(243, 200, 75), width=8)
        x = left + index * gap
        draw.line((x, top, x, top + gap * 3), fill=(255, 94, 98), width=8)
    save_png(image, ASSETS / "games" / "square_xo" / "thumbnails" / "card.png")


def create_nuts_and_bolts_thumbnail() -> None:
    image = card_base((232, 228, 218), (105, 108, 112))
    draw = ImageDraw.Draw(image)
    xs = (190, 285, 380, 475)
    nut_colors = [(218, 79, 76), (64, 129, 207), (229, 184, 61), (72, 166, 103)]
    for index, x in enumerate(xs):
        draw.line((x, 92, x, 278), fill=(74, 76, 80), width=16)
        draw.ellipse((x - 14, 78, x + 14, 106), fill=(184, 188, 190))
        draw.rounded_rectangle((x - 42, 276, x + 42, 304), radius=10, fill=(105, 108, 112))
        for stack in range(3):
            y = 246 - stack * 42
            color = nut_colors[(index + stack) % len(nut_colors)]
            draw.rounded_rectangle((x - 36, y - 14, x + 36, y + 14), radius=10, fill=color)
            draw.ellipse((x - 12, y - 8, x + 12, y + 8), fill=(54, 55, 57))
    save_png(image, ASSETS / "games" / "nuts_and_bolts" / "thumbnails" / "card.png")


def card_base(primary: tuple[int, int, int], secondary: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", THUMB_SIZE, (*primary, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((22, 22, 618, 338), radius=36, fill=(*secondary, 75), outline=(255, 255, 255, 180), width=4)
    draw.ellipse((-100, -120, 240, 220), fill=(255, 255, 255, 42))
    draw.ellipse((420, 180, 760, 520), fill=(255, 255, 255, 34))
    return image


def save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, optimize=True)


def write_manifest() -> None:
    entries = []
    for path in sorted(ASSETS.rglob("*")):
        if not path.is_file() or path.name == "manifest.json":
            continue
        entries.append(
            {
                "path": path.relative_to(ASSETS).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": sha256(path),
                "license": license_for(path),
            }
        )
    (ASSETS / "manifest.json").write_text(json.dumps({"assets": entries}, indent=2) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def license_for(path: Path) -> str:
    relative = path.relative_to(ASSETS).as_posix()
    if relative.startswith("audio/"):
        return "Third-party audio; see project provenance before redistribution"
    if relative.startswith(("source_branding/", "branding/", "backgrounds/")):
        return "Provided Game Game Go branding asset"
    if relative.startswith("games/color_wars/images/"):
        return "Legacy Color Wars project asset"
    if path.suffix.lower() == ".png":
        return "Project-created"
    return "Project documentation"


if __name__ == "__main__":
    raise SystemExit(main())
