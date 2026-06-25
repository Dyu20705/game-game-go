"""JSON save/load service for platform settings."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile


class SaveService:
    """Read and write versioned platform save documents."""

    def __init__(self, save_path: Path):
        self.save_path = Path(save_path)

    def load(self) -> dict[str, object]:
        if not self.save_path.exists():
            return {}
        try:
            with self.save_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            return {}
        return data if isinstance(data, dict) else {}

    def save(self, document: dict[str, object]):
        self.save_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile("w", encoding="utf-8", dir=self.save_path.parent, delete=False) as handle:
            json.dump(document, handle, ensure_ascii=False, indent=2)
            temp_path = Path(handle.name)
        temp_path.replace(self.save_path)
