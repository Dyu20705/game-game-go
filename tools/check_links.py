"""Check local Markdown links used by README and docs."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")
EXTERNAL_SCHEMES = {"http", "https", "mailto"}


def iter_markdown_files() -> list[Path]:
    return sorted([ROOT / "README.md", *ROOT.glob("docs/**/*.md"), *ROOT.glob("docker/**/*.md")])


def normalize_target(raw: str) -> str:
    target = raw.strip().split()[0]
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    return target


def main() -> int:
    failures: list[str] = []
    for path in iter_markdown_files():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for match in LINK_PATTERN.finditer(text):
            raw_target = normalize_target(match.group(1))
            parsed = urlparse(raw_target)
            if parsed.scheme in EXTERNAL_SCHEMES or raw_target.startswith("#"):
                continue
            local = unquote(parsed.path)
            if not local:
                continue
            target_path = (path.parent / local).resolve()
            try:
                target_path.relative_to(ROOT)
            except ValueError:
                failures.append(f"{path.relative_to(ROOT)} links outside repo: {raw_target}")
                continue
            if not target_path.exists():
                failures.append(f"{path.relative_to(ROOT)} missing link target: {raw_target}")

    if failures:
        print("Markdown link check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Markdown link check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
