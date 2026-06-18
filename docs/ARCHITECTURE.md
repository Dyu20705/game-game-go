# Architecture

Game Game Go dùng kiến trúc platform shell + mini-game contract. Platform quản lý lifecycle cấp cao; từng mini-game tự sở hữu gameplay loop, state, input mapping và render đặc thù.

## Dependency Rule

```text
platform must not depend on games.color_wars internals
games may depend on public platform contracts/services
games must not depend on other games
legacy compatibility modules may re-export old Color Wars paths during migration
```

## Platform

`src/platform` gồm:

- `games`: contract, descriptor, launch options, exit result, registry.
- `context.py`: `PlatformContext` truyền screen, clock và services vào mini-game.
- `services`: settings, save, audio, localization, asset resolver.
- `scenes`: home, game library, settings, about, scene result/action.
- `ui`: shared button/text/layout/theme/icon helpers.
- `app.py`: boot Pygame, tạo context, chạy scene flow và launch game qua registry.

Scene flow hiện tại là transitional blocking flow:

```text
HOME
  -> GAME_LIBRARY
      -> COLOR_WARS launch options -> ColorWarsSession.run()
      -> SQUARE_XO launch options -> SquareXOLocalSession.run()
      -> DEMO_GAME session -> DemoGameSession.run()
  -> SETTINGS
  -> ABOUT
  -> QUIT
```

Thiết kế này giữ rủi ro thấp vì Color Wars vốn đã dùng blocking `run_game()`. Platform vẫn nhận lại `GameExitResult` rõ ràng sau mỗi session.

## Game Contract

Mini-game implement:

- `descriptor`: metadata typed bằng `GameDescriptor`.
- `create_session(context, launch_options)`: tạo `GameSession`.
- `GameSession.run()`: chạy tới khi trả `GameExitResult`.

Contract dùng `typing.Protocol` thay vì base class để nhẹ và linh hoạt. Game không bị buộc kế thừa framework class hoặc dùng cùng model state.

## Registry

`GameRegistry` là nguồn dữ liệu duy nhất cho danh sách game. Registry:

- từ chối `game_id` trùng;
- lấy game theo ID;
- liệt kê enabled games;
- sort ổn định bằng `sort_order`, `title`, `game_id`;
- báo lỗi rõ khi game không tồn tại.

Đăng ký hiện là static trong `build_default_registry()`. Cấu trúc đủ để sau này chuyển sang manifest discovery.

## Services

Platform settings tách khỏi launch options/game preferences:

- `PlatformSettings`: fullscreen, sound, master volume, language, window size.
- `SettingsService.games`: namespace riêng cho preference từng game.
- `SaveService`: JSON versioned document, fallback khi thiếu/hỏng file, atomic replace.
- `AudioService`: wrapper nhỏ quanh pygame mixer, chịu lỗi mixer/file thiếu.
- `LocalizationService`: key-based VI/EN cho platform text.
- `AssetService`: resolver platform/game/legacy asset bằng `pathlib`.

## Blockchain/Oasis Layer

`src/platform/blockchain` defines public ports and local adapters. Games depend
on these ports, not raw RPC, ABI, wallet, Sapphire SDK, or ROFL clients.

Local mode is the default implementation for development and tests. Oasis
testnet adapters are explicit integration boundaries and are not required for
the platform to boot or for local gameplay.

## Color Wars Ownership

Các phần vẫn thuộc Color Wars:

- board/dots/winner logic;
- explosion BFS;
- PvP/PvBot;
- AI easy/medium/hard;
- board layout và mouse-to-cell mapping;
- HUD, tutorial luật Color Wars, win overlay;
- animation nổ dây chuyền.

Các phần shared mới thuộc platform:

- app shell;
- registry/contract;
- platform settings/save/audio/localization/assets;
- home/library/settings/about platform scenes.
