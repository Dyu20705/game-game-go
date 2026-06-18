"""Color contrast helpers for readable UI text."""


def _linearize(channel: float) -> float:
    value = channel / 255.0
    if value <= 0.03928:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def relative_luminance(color: tuple[int, int, int]) -> float:
    r, g, b = color
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def contrast_ratio(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    l1 = relative_luminance(c1)
    l2 = relative_luminance(c2)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def ensure_readable_text(bg: tuple[int, int, int], preferred=(24, 28, 33), min_ratio: float = 4.5) -> tuple[int, int, int]:
    """Return preferred text color if readable, else fallback to black/white."""
    if contrast_ratio(bg, preferred) >= min_ratio:
        return preferred
    dark = (24, 28, 33)
    light = (250, 248, 242)
    return dark if contrast_ratio(bg, dark) >= contrast_ratio(bg, light) else light


def suggest_safe_palette() -> dict[str, tuple[int, int, int]]:
    """Small safe palette suitable for light-background UI."""
    return {
        "surface": (248, 243, 232),
        "surface_alt": (235, 226, 211),
        "text": (29, 35, 42),
        "primary": (54, 126, 177),
        "danger": (186, 78, 78),
        "success": (70, 145, 103),
    }


