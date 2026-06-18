"""Main entry point for Game Game Go."""

import sys

if __package__ is None or __package__ == "":
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.platform.app import main as run_platform


def main():
    """Run the Game Game Go platform."""

    return run_platform()

if __name__ == "__main__":
    main()
