"""Asset resolver and bounded runtime cache for Game Game Go."""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AssetCacheStats:
    image_hits: int = 0
    image_misses: int = 0
    scaled_hits: int = 0
    scaled_misses: int = 0
    font_hits: int = 0
    font_misses: int = 0


class AssetService:
    """Resolve and load assets without depending on the current working directory."""

    def __init__(
        self,
        repository_root: Path,
        *,
        max_images: int = 64,
        max_scaled_images: int = 128,
        max_fonts: int = 64,
    ):
        self.repository_root = Path(repository_root)
        self.assets_root = self.repository_root / "assets"
        self.max_images = max_images
        self.max_scaled_images = max_scaled_images
        self.max_fonts = max_fonts
        self._image_cache: OrderedDict[Path, Any] = OrderedDict()
        self._scaled_cache: OrderedDict[tuple[Path, tuple[int, int], bool], Any] = OrderedDict()
        self._cover_cache: OrderedDict[tuple[Path, tuple[int, int], tuple[float, float], bool], Any] = OrderedDict()
        self._font_cache: OrderedDict[tuple[str, int, bool, bool], Any] = OrderedDict()
        self._stats = {
            "image_hits": 0,
            "image_misses": 0,
            "scaled_hits": 0,
            "scaled_misses": 0,
            "font_hits": 0,
            "font_misses": 0,
        }

    def brand(self, relative_path: str | Path) -> Path:
        return self.branding(relative_path)

    def branding(self, relative_path: str | Path) -> Path:
        return self._asset_path("branding", relative_path)

    def background(self, relative_path: str | Path) -> Path:
        return self._asset_path("backgrounds", relative_path)

    def platform(self, relative_path: str | Path) -> Path:
        return self._asset_path("platform", relative_path)

    def audio(self, relative_path: str | Path) -> Path:
        return self._asset_path("audio", relative_path)

    def game(self, game_id: str, relative_path: str | Path) -> Path:
        return self._asset_path("games", game_id, relative_path)

    def fallback_image(self) -> Path:
        return self.platform("fallbacks/game_thumbnail.png")

    def resolve(self, path: str | Path | None) -> Path | None:
        if path is None:
            return None
        candidate = Path(path)
        if candidate.is_absolute():
            return candidate
        return self.assets_root / candidate

    def legacy(self, relative_path: str | Path) -> Path:
        """Compatibility shim for old callers; TODO remove after Color Wars legacy modules are retired."""

        text = Path(relative_path).as_posix()
        if text.startswith("aud/"):
            return self.audio(text.removeprefix("aud/"))
        if text.startswith("img/color-wars/"):
            return self.game("color_wars", "images") / text.removeprefix("img/color-wars/")
        if text.startswith("img/"):
            return self.platform(text.removeprefix("img/"))
        return self.assets_root / text

    def image(self, pygame, path: str | Path | None, *, fallback_size: tuple[int, int] = (96, 96)):
        resolved = self.resolve(path)
        if resolved is not None and resolved.exists():
            key = resolved.resolve()
            cached = self._get_lru(self._image_cache, key)
            if cached is not None:
                self._stats["image_hits"] += 1
                return cached
            self._stats["image_misses"] += 1
            try:
                surface = pygame.image.load(str(key))
                try:
                    surface = surface.convert_alpha()
                except pygame.error:
                    surface = surface.copy()
                self._put_lru(self._image_cache, key, surface, self.max_images)
                return surface
            except (pygame.error, OSError):
                pass
        self._stats["image_misses"] += 1
        return self.placeholder_surface(pygame, fallback_size)

    def scaled_image(
        self,
        pygame,
        path: str | Path | None,
        size: tuple[int, int],
        *,
        smooth: bool = True,
    ):
        width, height = max(1, int(size[0])), max(1, int(size[1]))
        resolved = self.resolve(path)
        key_path = resolved.resolve() if resolved is not None and resolved.exists() else self.fallback_image()
        key = (key_path, (width, height), smooth)
        cached = self._get_lru(self._scaled_cache, key)
        if cached is not None:
            self._stats["scaled_hits"] += 1
            return cached

        self._stats["scaled_misses"] += 1
        source = self.image(pygame, resolved, fallback_size=(width, height))
        transform = pygame.transform.smoothscale if smooth else pygame.transform.scale
        scaled = transform(source, (width, height))
        self._put_lru(self._scaled_cache, key, scaled, self.max_scaled_images)
        return scaled

    def cover_image(
        self,
        pygame,
        path: str | Path | None,
        size: tuple[int, int],
        *,
        focal: tuple[float, float] = (0.5, 0.5),
        smooth: bool = True,
    ):
        width, height = max(1, int(size[0])), max(1, int(size[1]))
        resolved = self.resolve(path)
        key_path = resolved.resolve() if resolved is not None and resolved.exists() else self.fallback_image()
        focal = (min(1.0, max(0.0, float(focal[0]))), min(1.0, max(0.0, float(focal[1]))))
        key = (key_path, (width, height), focal, smooth)
        cached = self._get_lru(self._cover_cache, key)
        if cached is not None:
            self._stats["scaled_hits"] += 1
            return cached

        self._stats["scaled_misses"] += 1
        source = self.image(pygame, resolved, fallback_size=(width, height))
        scale = max(width / source.get_width(), height / source.get_height())
        scaled_size = (
            max(width, int(source.get_width() * scale + 0.5)),
            max(height, int(source.get_height() * scale + 0.5)),
        )
        transform = pygame.transform.smoothscale if smooth else pygame.transform.scale
        scaled = transform(source, scaled_size)
        max_left = max(0, scaled.get_width() - width)
        max_top = max(0, scaled.get_height() - height)
        crop = pygame.Rect(int(max_left * focal[0]), int(max_top * focal[1]), width, height)
        covered = scaled.subsurface(crop).copy()
        self._put_lru(self._cover_cache, key, covered, self.max_scaled_images)
        return covered

    def font(self, pygame, font_id: str = "body", size: int = 16, *, bold: bool = False, italic: bool = False):
        key = (font_id, int(size), bool(bold), bool(italic))
        cached = self._get_lru(self._font_cache, key)
        if cached is not None:
            self._stats["font_hits"] += 1
            return cached

        self._stats["font_misses"] += 1
        font_path = self._asset_path("fonts", f"{font_id}.ttf")
        try:
            if font_path.exists():
                font = pygame.font.Font(str(font_path), int(size))
            else:
                font = pygame.font.SysFont(["segoeui", "arial", "dejavusans"], int(size), bold=bold, italic=italic)
        except (pygame.error, OSError):
            font = pygame.font.Font(None, int(size))
        self._put_lru(self._font_cache, key, font, self.max_fonts)
        return font

    def placeholder_surface(self, pygame, size: tuple[int, int] = (96, 96)):
        width, height = max(1, int(size[0])), max(1, int(size[1]))
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill((35, 185, 211, 255))
        pygame.draw.rect(
            surface, (255, 255, 255, 190), surface.get_rect(), 2, border_radius=max(4, min(width, height) // 12)
        )
        pygame.draw.circle(surface, (255, 190, 75), (width // 2, height // 2), max(8, min(width, height) // 5))
        pygame.draw.circle(surface, (255, 94, 98), (width // 2, height // 2), max(3, min(width, height) // 12))
        return surface

    @property
    def stats(self) -> AssetCacheStats:
        return AssetCacheStats(**self._stats)

    def cache_sizes(self) -> dict[str, int]:
        return {
            "images": len(self._image_cache),
            "scaled_images": len(self._scaled_cache),
            "cover_images": len(self._cover_cache),
            "fonts": len(self._font_cache),
        }

    def _asset_path(self, *parts: str | Path) -> Path:
        return self.assets_root.joinpath(*(str(part) for part in parts))

    @staticmethod
    def _get_lru(cache: OrderedDict, key):
        if key not in cache:
            return None
        value = cache.pop(key)
        cache[key] = value
        return value

    @staticmethod
    def _put_lru(cache: OrderedDict, key, value, limit: int) -> None:
        if key in cache:
            cache.pop(key)
        cache[key] = value
        while len(cache) > limit:
            cache.popitem(last=False)
