from src.platform.services import SaveService


def test_save_service_returns_empty_document_for_missing_file(tmp_path):
    service = SaveService(tmp_path / "missing.json")

    assert service.load() == {}


def test_save_service_handles_corrupt_json(tmp_path):
    save_path = tmp_path / "settings.json"
    save_path.write_text("{broken", encoding="utf-8")

    assert SaveService(save_path).load() == {}


def test_save_service_round_trips_document(tmp_path):
    save_path = tmp_path / "settings.json"
    service = SaveService(save_path)

    service.save({"schema_version": 1, "platform": {"language": "en"}})

    assert service.load()["platform"]["language"] == "en"
