"""Audit Python package dependencies under src and tests.

The script intentionally uses AST imports instead of filename heuristics so it
can flag boundary violations even when packages are renamed during migration.
"""

from __future__ import annotations

import ast
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
TESTS_ROOT = REPO_ROOT / "tests"

LEGACY_ROOT_PACKAGES = ("src.ai", "src.engine", "src.game", "src.view")
LEGACY_ROOT_PATHS = ("src/ai", "src/engine", "src/game", "src/view")
GAME_NAMES = {"color_wars", "demo_game", "nuts_and_bolts", "square_xo"}
DOMAIN_MARKERS = (".domain", ".engine", ".rules", ".models", ".level_generator")


@dataclass(frozen=True)
class ImportEdge:
    importer: str
    imported: str
    file: Path
    line: int


@dataclass(frozen=True)
class AuditResult:
    modules: tuple[str, ...]
    edges: tuple[ImportEdge, ...]
    cycles: tuple[tuple[str, ...], ...]
    legacy_imports: tuple[ImportEdge, ...]
    platform_game_violations: tuple[ImportEdge, ...]
    game_game_violations: tuple[ImportEdge, ...]
    domain_pygame_violations: tuple[ImportEdge, ...]
    duplicate_modules: tuple[tuple[str, str], ...]
    orphan_modules: tuple[str, ...]
    large_modules: tuple[tuple[str, int], ...]
    public_api: tuple[str, ...]


def iter_python_files(*roots: Path) -> Iterable[Path]:
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if "__pycache__" not in path.parts:
                yield path


def module_name(path: Path) -> str:
    rel = path.relative_to(REPO_ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_import_edges(path: Path) -> list[ImportEdge]:
    source = path.read_text(encoding="utf-8")
    module = module_name(path)
    is_package = path.stem == "__init__"
    tree = ast.parse(source, filename=str(path))
    edges: list[ImportEdge] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                edges.append(ImportEdge(module, alias.name, path, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            imported = resolve_import_from(module, node, is_package)
            if imported:
                edges.append(ImportEdge(module, imported, path, node.lineno))
    return edges


def resolve_import_from(module: str, node: ast.ImportFrom, is_package: bool = False) -> str | None:
    if node.level == 0:
        return node.module
    package_parts = module.split(".")
    base = package_parts if is_package else package_parts[:-1]
    if node.level > 1:
        base = base[: max(0, len(base) - node.level + 1)]
    if node.module:
        base.extend(node.module.split("."))
    return ".".join(part for part in base if part)


def source_edges(edges: Iterable[ImportEdge]) -> tuple[ImportEdge, ...]:
    return tuple(edge for edge in edges if edge.importer.startswith("src.") and edge.imported.startswith("src."))


def package_level(module: str, depth: int = 3) -> str:
    parts = module.split(".")
    return ".".join(parts[: min(depth, len(parts))])


def detect_cycles(edges: Iterable[ImportEdge]) -> tuple[tuple[str, ...], ...]:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in source_edges(edges):
        importer = package_level(edge.importer)
        imported = package_level(edge.imported)
        if importer != imported:
            graph[importer].add(imported)

    cycles: set[tuple[str, ...]] = set()

    def visit(node: str, stack: list[str]) -> None:
        if node in stack:
            cycle = stack[stack.index(node) :] + [node]
            rotations = [tuple(cycle[i:-1] + cycle[:i] + [cycle[i]]) for i in range(len(cycle) - 1)]
            cycles.add(min(rotations))
            return
        if len(stack) > 12:
            return
        for next_node in graph.get(node, ()):
            visit(next_node, stack + [node])

    for node in sorted(graph):
        visit(node, [])
    return tuple(sorted(cycles))


def game_name(module: str) -> str | None:
    parts = module.split(".")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "games" and parts[2] in GAME_NAMES:
        return parts[2]
    return None


def is_platform_game_violation(edge: ImportEdge) -> bool:
    if not edge.importer.startswith("src.platform."):
        return False
    if edge.importer.startswith("src.platform.bootstrap."):
        return False
    if not edge.imported.startswith("src.games."):
        return False
    parts = edge.imported.split(".")
    return len(parts) > 4 or (len(parts) >= 4 and parts[3] not in {"game", "manifest"})


def is_domain_module(module: str) -> bool:
    return any(marker in module for marker in DOMAIN_MARKERS)


def find_duplicate_modules(modules: Iterable[str]) -> tuple[tuple[str, str], ...]:
    duplicates: list[tuple[str, str]] = []
    module_set = set(modules)
    mapping = {
        "src.ai": "src.games.color_wars.ai",
        "src.engine": "src.games.color_wars.engine",
        "src.game": "src.games.color_wars.runtime",
        "src.view": "src.games.color_wars.view",
    }
    for old_prefix, new_prefix in mapping.items():
        for module in sorted(module_set):
            if module == old_prefix or module.startswith(old_prefix + "."):
                counterpart = new_prefix + module[len(old_prefix) :]
                if counterpart in module_set:
                    duplicates.append((module, counterpart))
    return tuple(duplicates)


def collect_public_api() -> tuple[str, ...]:
    api_path = SRC_ROOT / "platform" / "games" / "__init__.py"
    if not api_path.exists():
        return ()
    tree = ast.parse(api_path.read_text(encoding="utf-8"), filename=str(api_path))
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if (
                    isinstance(target, ast.Name)
                    and target.id == "__all__"
                    and isinstance(node.value, (ast.List, ast.Tuple))
                ):
                    for item in node.value.elts:
                        if isinstance(item, ast.Constant) and isinstance(item.value, str):
                            names.append(item.value)
    return tuple(sorted(names))


def audit() -> AuditResult:
    files = tuple(iter_python_files(SRC_ROOT, TESTS_ROOT))
    modules = tuple(sorted(module_name(path) for path in files))
    edges = tuple(edge for path in files for edge in parse_import_edges(path))
    incoming = Counter(edge.imported for edge in source_edges(edges))

    legacy_imports = tuple(
        edge
        for edge in edges
        if edge.imported in LEGACY_ROOT_PACKAGES
        or any(edge.imported.startswith(prefix + ".") for prefix in LEGACY_ROOT_PACKAGES)
    )
    platform_game_violations = tuple(edge for edge in edges if is_platform_game_violation(edge))
    game_game_violations = tuple(
        edge
        for edge in edges
        if (src_game := game_name(edge.importer)) and (dst_game := game_name(edge.imported)) and src_game != dst_game
    )
    domain_pygame_violations = tuple(
        edge for edge in edges if is_domain_module(edge.importer) and edge.imported == "pygame"
    )
    duplicate_modules = find_duplicate_modules(modules)
    orphan_modules = tuple(
        module
        for module in modules
        if module.startswith("src.")
        and module not in {"src.main"}
        and incoming[module] == 0
        and not module.endswith("__init__")
        and not module.endswith(".manifest")
        and not module.endswith(".game")
    )
    large_modules = tuple(
        sorted(
            (
                (module_name(path), len(path.read_text(encoding="utf-8").splitlines()))
                for path in files
                if path.is_relative_to(SRC_ROOT) and len(path.read_text(encoding="utf-8").splitlines()) >= 250
            ),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    return AuditResult(
        modules=modules,
        edges=edges,
        cycles=detect_cycles(edges),
        legacy_imports=legacy_imports,
        platform_game_violations=platform_game_violations,
        game_game_violations=game_game_violations,
        domain_pygame_violations=domain_pygame_violations,
        duplicate_modules=duplicate_modules,
        orphan_modules=orphan_modules,
        large_modules=large_modules,
        public_api=collect_public_api(),
    )


def format_edge(edge: ImportEdge) -> str:
    rel = edge.file.relative_to(REPO_ROOT).as_posix()
    return f"`{edge.importer}` -> `{edge.imported}` ({rel}:{edge.line})"


def markdown_report(result: AuditResult) -> str:
    package_counts = Counter(package_level(module, 3) for module in result.modules if module.startswith("src."))
    compatibility_count = len(result.legacy_imports)
    lines = [
        "# Source Dependency Audit",
        "",
        "Generated by `py tools/src_dependency_audit.py`.",
        "",
        "## Package Tree",
        "",
    ]
    for package, count in sorted(package_counts.items()):
        lines.append(f"- `{package}`: {count} modules")

    sections: list[tuple[str, Iterable[str]]] = [
        ("Import Graph", (format_edge(edge) for edge in source_edges(result.edges))),
        ("Cycles", (" -> ".join(f"`{item}`" for item in cycle) for cycle in result.cycles)),
        ("Legacy Aliases", (f"`{old}` -> `{new}`" for old, new in result.duplicate_modules)),
        ("Duplicate Modules", (f"`{old}` duplicates `{new}`" for old, new in result.duplicate_modules)),
        ("Orphan Modules", (f"`{module}`" for module in result.orphan_modules)),
        ("Platform -> Game Violations", (format_edge(edge) for edge in result.platform_game_violations)),
        ("Game -> Game Violations", (format_edge(edge) for edge in result.game_game_violations)),
        ("Domain -> Pygame Violations", (format_edge(edge) for edge in result.domain_pygame_violations)),
        ("Large Modules", (f"`{module}`: {line_count} lines" for module, line_count in result.large_modules)),
        ("Public API", (f"`{name}`" for name in result.public_api)),
    ]

    lines.extend(
        [
            "",
            "## Compatibility Usage Count",
            "",
            f"- Legacy root import count: `{compatibility_count}`",
            "",
        ]
    )

    for title, items in sections:
        lines.append(f"## {title}")
        lines.append("")
        materialized = list(items)
        if materialized:
            lines.extend(f"- {item}" for item in materialized[:200])
            if len(materialized) > 200:
                lines.append(f"- ... {len(materialized) - 200} more")
        else:
            lines.append("- None")
        lines.append("")

    lines.extend(
        [
            "## Class/Function Ownership",
            "",
            "- Platform contracts live in `src.platform.games`.",
            "- Color Wars AI/rules/runtime/presentation live in `src.games.color_wars`.",
            "- SquareXO deterministic rules/replay live in `src.games.square_xo.domain` and verifier orchestration in application/infrastructure modules.",
            "- Nuts & Bolts rules/generator/session remain owned by `src.games.nuts_and_bolts`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    report = markdown_report(audit())
    output = REPO_ROOT / "docs" / "SRC_DEPENDENCY_AUDIT.md"
    output.write_text(report + "\n", encoding="utf-8")
    print(f"Wrote {output.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
