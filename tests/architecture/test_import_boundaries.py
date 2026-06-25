from pathlib import Path

from tools.src_dependency_audit import LEGACY_ROOT_PATHS, audit


def test_legacy_color_wars_root_modules_are_removed():
    repo_root = Path(__file__).resolve().parents[2]

    for legacy_path in LEGACY_ROOT_PATHS:
        assert not (repo_root / legacy_path).exists(), legacy_path
    assert not (repo_root / "src" / "controller.py").exists()


def test_no_legacy_root_imports_remain():
    result = audit()

    assert result.legacy_imports == ()


def test_platform_imports_only_public_game_adapters_outside_bootstrap():
    result = audit()

    assert result.platform_game_violations == ()


def test_games_do_not_import_other_games():
    result = audit()

    assert result.game_game_violations == ()


def test_domain_packages_do_not_import_pygame():
    result = audit()

    assert result.domain_pygame_violations == ()


def test_source_package_graph_has_no_cycles():
    result = audit()

    assert result.cycles == ()


def test_platform_games_public_api_is_explicit():
    result = audit()

    assert set(result.public_api) == {
        "DuplicateGameError",
        "GameCapability",
        "GameDescriptor",
        "GameExitAction",
        "GameExitResult",
        "GameLaunchOptions",
        "GameModule",
        "GameNotFoundError",
        "GameRegistry",
        "GameSession",
    }
