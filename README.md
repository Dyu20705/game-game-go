# Game Game Go

Game Game Go là nền tảng desktop đa mini-game viết bằng Python và Pygame. Dự án được refactor từ Color Wars: Color Wars hiện là mini-game đầu tiên, còn platform chịu trách nhiệm boot app, registry, game library, settings, audio, asset resolving và lifecycle chung.

## Mini-Games

- Color Wars: game chiến thuật theo lượt với PvP, PvBot, AI easy/medium/hard, HUD, tutorial, settings và animation nổ dây chuyền.
- Click Sprint: demo mini-game nhỏ để chứng minh platform có thể đăng ký và launch nhiều game qua cùng contract.

## Cài Đặt

Yêu cầu:

- Python 3.10+
- Pygame 2.x

```bash
pip install -r requirements.txt
```

## Chạy Ứng Dụng

```bash
python -m src.main
```

Entry point này khởi động Game Game Go, không khởi động trực tiếp Color Wars nữa.

## Chạy Test

```bash
pytest -q
```

Trong môi trường sandbox hiện tại, `py -m pytest ... -p no:cacheprovider` được dùng để tránh lỗi ghi cache ngoài workspace.

## Cấu Trúc Mức Cao

```text
src/
  main.py                    Entry point Game Game Go.
  platform/                  Platform shell, registry, contract, services, scenes, UI.
  games/
    color_wars/              Color Wars mini-game package và adapter.
    demo_game/               Click Sprint demo mini-game.
  ai/, engine/, game/, view/  Compatibility modules cũ của Color Wars.
tests/
  platform/                  Tests cho registry, settings, save, assets, lifecycle.
  games/                     Tests contract/lifecycle cho mini-game.
  ai/, game_logic/, game/, view/
                             Test cũ của Color Wars.
docs/
  ARCHITECTURE.md
  GAME_INTEGRATION_GUIDE.md
  COLOR_WARS_MIGRATION.md
  DEVELOPMENT.md
  TESTING.md
  ROADMAP.md
```

## Tài Liệu

- [Architecture](docs/ARCHITECTURE.md)
- [Game Integration Guide](docs/GAME_INTEGRATION_GUIDE.md)
- [Color Wars Migration](docs/COLOR_WARS_MIGRATION.md)
- [Development](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Roadmap](docs/ROADMAP.md)

## License

Dự án dùng giấy phép MIT. Xem [LICENSE](LICENSE).

