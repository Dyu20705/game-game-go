# Development

## Local Setup

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
python -m src.main
```

## Test

```bash
pytest -q
```

Trong sandbox hiện tại:

```bash
py -m pytest tests\platform tests\games -q -p no:cacheprovider
py -m pytest tests\game_logic tests\ai -q -p no:cacheprovider
py -m compileall -q src tests
```

## Development Rules

- Platform không import engine/state/AI nội bộ của Color Wars.
- Game phụ thuộc public platform contract/service, không phụ thuộc game khác.
- Gameplay-specific logic ở lại package game.
- Settings global thuộc platform; difficulty/mode thuộc launch options hoặc game-specific preferences.
- Không thêm dependency runtime nếu standard library và Pygame đủ dùng.

## Save Data

Settings được lưu qua `SaveService` vào đường dẫn cấu hình trong `PlatformConfig.save_path`, mặc định:

```text
~/.game_game_go/settings.json
```

Format:

```json
{
  "schema_version": 1,
  "platform": {
    "fullscreen": false,
    "sound_enabled": true,
    "master_volume": 0.8,
    "language": "vi",
    "window_size": [1100, 720]
  },
  "games": {
    "color_wars": {
      "last_mode": "pvbot",
      "last_difficulty": "easy"
    }
  }
}
```

