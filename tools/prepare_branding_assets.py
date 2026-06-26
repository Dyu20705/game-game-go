"""Prepare Chillody Studio and Game Game Go branding assets for runtime."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "source_branding"
LEGACY = ASSETS / "brand"
BRANDING = ASSETS / "branding"
BACKGROUNDS = ASSETS / "backgrounds"

SOURCE_FILES = {
    "chillody-studio-source.png": "chillody.png",
    "game-game-go-logo-source.png": "app_icon_master.png",
    "game-game-go-background-vertical-source.png": "background.png",
}


def main() -> None:
    SOURCE.mkdir(parents=True, exist_ok=True)
    BRANDING.mkdir(parents=True, exist_ok=True)
    BACKGROUNDS.mkdir(parents=True, exist_ok=True)
    _ensure_sources()

    studio_source = Image.open(SOURCE / "chillody-studio-source.png").convert("RGBA")
    logo_source = Image.open(SOURCE / "game-game-go-logo-source.png").convert("RGBA")
    background_source = Image.open(SOURCE / "game-game-go-background-vertical-source.png").convert("RGB")

    studio = _crop_to_visual_bounds(studio_source, threshold=18, padding_ratio=0.055)
    studio.save(BRANDING / "studio_logo.png", optimize=True)
    studio.resize((320, 320), Image.Resampling.LANCZOS).save(BRANDING / "studio_logo_runtime.png", optimize=True)

    logo_alpha = _remove_connected_white_background(logo_source)
    logo_full = _crop_to_alpha_bounds(logo_alpha, padding_ratio=0.065)
    logo_full.save(BRANDING / "game_logo_full.png", optimize=True)
    logo_full.thumbnail((760, 360), Image.Resampling.LANCZOS)
    logo_full.save(BRANDING / "game_logo_full_runtime.png", optimize=True)

    symbol = _crop_symbol(logo_alpha)
    symbol.save(BRANDING / "game_logo_symbol.png", optimize=True)
    for size in (64, 128, 256, 512):
        icon = _square_icon(symbol, size)
        icon.save(BRANDING / f"app_icon_{size}.png", optimize=True)
    _square_icon(symbol, 256).save(BRANDING / "app_icon.png", optimize=True)
    _square_icon(symbol, 256).save(
        BRANDING / "app_icon.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    )

    menu_bg = _compose_wide_background(background_source)
    menu_bg.save(BACKGROUNDS / "menu_background_1920x1080.png", optimize=True)
    menu_bg.resize((480, 270), Image.Resampling.LANCZOS).save(
        BACKGROUNDS / "menu_background_preview.png", optimize=True
    )

    hero = _compose_readme_hero(menu_bg)
    hero.save(BRANDING / "hero_banner.png", optimize=True)
    social = _compose_social_preview(menu_bg)
    social.save(BRANDING / "github_social_preview.png", optimize=True)

    _write_brand_manifest()


def _ensure_sources() -> None:
    for target_name, legacy_name in SOURCE_FILES.items():
        target = SOURCE / target_name
        if not target.exists():
            source = LEGACY / legacy_name
            if not source.exists():
                raise FileNotFoundError(f"Missing source branding asset: {source}")
            shutil.copy2(source, target)


def _crop_to_visual_bounds(image: Image.Image, *, threshold: int, padding_ratio: float) -> Image.Image:
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")
    if alpha.getextrema() != (255, 255):
        bbox = alpha.getbbox()
    else:
        rgb = rgba.convert("RGB")
        corners = [
            rgb.getpixel((0, 0)),
            rgb.getpixel((rgb.width - 1, 0)),
            rgb.getpixel((0, rgb.height - 1)),
            rgb.getpixel((rgb.width - 1, rgb.height - 1)),
        ]
        bg = tuple(sum(channel) // len(corners) for channel in zip(*corners))
        diff = ImageChops.difference(rgb, Image.new("RGB", rgb.size, bg)).convert("L")
        mask = diff.point(lambda px: 255 if px > threshold else 0)
        bbox = mask.getbbox()
    if bbox is None:
        return rgba
    return _crop_with_padding(rgba, bbox, padding_ratio)


def _remove_connected_white_background(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    rgb = rgba.convert("RGB")
    near_white = Image.new("L", rgba.size, 0)
    near_white_pixels = near_white.load()
    rgb_pixels = rgb.load()
    width, height = rgba.size
    for y in range(height):
        for x in range(width):
            r, g, b = rgb_pixels[x, y]
            if r > 238 and g > 238 and b > 238 and max(r, g, b) - min(r, g, b) < 12:
                near_white_pixels[x, y] = 255

    connected = Image.new("L", rgba.size, 0)
    connected_pixels = connected.load()
    queue = []
    for x in range(width):
        queue.extend(((x, 0), (x, height - 1)))
    for y in range(height):
        queue.extend(((0, y), (width - 1, y)))
    while queue:
        x, y = queue.pop()
        if x < 0 or y < 0 or x >= width or y >= height:
            continue
        if connected_pixels[x, y] or near_white_pixels[x, y] == 0:
            continue
        connected_pixels[x, y] = 255
        queue.extend(((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)))

    softened = connected.filter(ImageFilter.GaussianBlur(1.15))
    alpha = rgba.getchannel("A")
    new_alpha = ImageChops.subtract(alpha, softened)
    rgba.putalpha(new_alpha)
    return rgba


def _crop_to_alpha_bounds(image: Image.Image, *, padding_ratio: float) -> Image.Image:
    alpha = image.getchannel("A")
    bbox = alpha.point(lambda px: 255 if px > 10 else 0).getbbox()
    if bbox is None:
        return image
    return _crop_with_padding(image, bbox, padding_ratio)


def _crop_symbol(image: Image.Image) -> Image.Image:
    full = _crop_to_alpha_bounds(image, padding_ratio=0.02)
    alpha = full.getchannel("A")
    bbox = alpha.point(lambda px: 255 if px > 10 else 0).getbbox()
    if bbox is None:
        return full
    left, top, right, bottom = bbox
    symbol_bottom = top + int((bottom - top) * 0.66)
    symbol = full.crop((left, top, right, symbol_bottom))
    return _crop_to_alpha_bounds(symbol, padding_ratio=0.08)


def _square_icon(image: Image.Image, size: int) -> Image.Image:
    icon = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    source = image.copy()
    source.thumbnail((int(size * 0.84), int(size * 0.84)), Image.Resampling.LANCZOS)
    icon.alpha_composite(source, ((size - source.width) // 2, (size - source.height) // 2))
    return icon


def _compose_wide_background(source: Image.Image) -> Image.Image:
    target = (1920, 1080)
    cover = _cover_resize(source, target)
    cover = cover.filter(ImageFilter.GaussianBlur(10))
    cover = Image.blend(cover, Image.new("RGB", target, (247, 250, 255)), 0.12)

    clear = source.copy()
    clear.thumbnail((980, 1080), Image.Resampling.LANCZOS)
    clear_layer = Image.new("RGBA", target, (0, 0, 0, 0))
    clear_x = 760
    clear_y = (target[1] - clear.height) // 2
    mask = _soft_horizontal_mask(clear.size, edge=170, opacity=218)
    clear_layer.alpha_composite(clear.convert("RGBA"), (clear_x, clear_y))
    clear_alpha = Image.new("L", target, 0)
    clear_alpha.paste(mask, (clear_x, clear_y))
    clear_layer.putalpha(clear_alpha)

    base = cover.convert("RGBA")
    _draw_soft_shapes(base)
    base.alpha_composite(clear_layer)
    overlay = Image.new("RGBA", target, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((112, 116, 780, 900), radius=72, fill=(255, 255, 255, 88))
    draw.rounded_rectangle((142, 146, 760, 872), radius=64, outline=(255, 255, 255, 78), width=2)
    base.alpha_composite(overlay)
    return base.convert("RGB")


def _draw_soft_shapes(base: Image.Image) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    shapes = (
        ((-180, 90, 520, 790), (41, 207, 230, 96)),
        ((-70, 640, 560, 1260), (132, 93, 255, 86)),
        ((1180, -130, 2060, 610), (255, 144, 190, 80)),
        ((1260, 510, 2150, 1230), (17, 195, 227, 98)),
        ((550, -260, 1220, 230), (112, 103, 255, 60)),
        ((610, 820, 1260, 1280), (255, 116, 186, 52)),
    )
    for box, color in shapes:
        draw.ellipse(box, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    base.alpha_composite(layer)


def _soft_horizontal_mask(size: tuple[int, int], *, edge: int, opacity: int) -> Image.Image:
    width, height = size
    mask = Image.new("L", size, 0)
    pixels = mask.load()
    for x in range(width):
        left = min(1.0, x / edge)
        right = min(1.0, (width - 1 - x) / edge)
        alpha = int(opacity * min(left, right))
        for y in range(height):
            pixels[x, y] = alpha
    vertical = Image.new("L", size, 0)
    draw = ImageDraw.Draw(vertical)
    draw.rounded_rectangle((0, 0, width, height), radius=140, fill=255)
    vertical = vertical.filter(ImageFilter.GaussianBlur(34))
    return ImageChops.multiply(mask, vertical)


def _compose_readme_hero(background: Image.Image) -> Image.Image:
    hero = _cover_resize(background, (1600, 520)).convert("RGBA")
    shade = Image.new("RGBA", hero.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(shade)
    draw.rounded_rectangle((74, 62, 640, 458), radius=56, fill=(255, 255, 255, 110))
    hero.alpha_composite(shade)
    logo = Image.open(BRANDING / "game_logo_full_runtime.png").convert("RGBA")
    logo.thumbnail((470, 230), Image.Resampling.LANCZOS)
    hero.alpha_composite(logo, (125, 130))
    return hero.convert("RGB")


def _compose_social_preview(background: Image.Image) -> Image.Image:
    preview = _cover_resize(background, (1280, 640)).convert("RGBA")
    logo = Image.open(BRANDING / "game_logo_full_runtime.png").convert("RGBA")
    logo.thumbnail((610, 300), Image.Resampling.LANCZOS)
    preview.alpha_composite(logo, (120, 160))
    studio = Image.open(BRANDING / "studio_logo_runtime.png").convert("RGBA")
    studio.thumbnail((140, 140), Image.Resampling.LANCZOS)
    preview.alpha_composite(studio, (1035, 430))
    return preview.convert("RGB")


def _cover_resize(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    width, height = size
    scale = max(width / image.width, height / image.height)
    resized = image.resize((int(image.width * scale + 0.5), int(image.height * scale + 0.5)), Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def _crop_with_padding(image: Image.Image, bbox: tuple[int, int, int, int], padding_ratio: float) -> Image.Image:
    left, top, right, bottom = bbox
    pad = int(max(right - left, bottom - top) * padding_ratio)
    return image.crop(
        (
            max(0, left - pad),
            max(0, top - pad),
            min(image.width, right + pad),
            min(image.height, bottom + pad),
        )
    )


def _write_brand_manifest() -> None:
    paths = [
        *sorted(SOURCE.glob("*.png")),
        *sorted(BRANDING.glob("*.png")),
        *sorted(BRANDING.glob("*.ico")),
        *sorted(BACKGROUNDS.glob("*.png")),
    ]
    data = {
        "studio": "Chillody Studio",
        "product": "Game Game Go",
        "generated_by": "tools/prepare_branding_assets.py",
        "assets": [_asset_record(path) for path in paths],
    }
    (ASSETS / "branding_manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _asset_record(path: Path) -> dict[str, str | int]:
    return {
        "path": path.relative_to(ASSETS).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "license": "Provided Game Game Go branding asset",
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generated_paths() -> Iterable[Path]:
    yield from SOURCE.glob("*.png")
    yield from BRANDING.glob("*")
    yield from BACKGROUNDS.glob("*")


if __name__ == "__main__":
    main()
