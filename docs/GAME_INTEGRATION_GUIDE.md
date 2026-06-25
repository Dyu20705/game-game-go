# Game Integration Guide

Tài liệu này mô tả cách thêm mini-game mới vào Game Game Go.

## 1. Tạo Package

```text
src/games/my_game/
  __init__.py
  manifest.py
  game.py
```

## 2. Khai Báo Descriptor

Trong `manifest.py`, tạo `GameDescriptor`:

```python
from src.platform.games import GameDescriptor

DESCRIPTOR = GameDescriptor(
    game_id="my_game",
    title="My Game",
    short_description="Short text for the library.",
    version="0.1.0",
    supported_modes=("solo",),
    enabled=True,
    sort_order=100,
)
```

`game_id` phải ổn định vì được dùng trong save data và registry.

## 3. Implement Contract

Trong `game.py`:

```python
from dataclasses import dataclass

from src.platform.games import GameExitAction, GameExitResult, GameLaunchOptions
from .manifest import DESCRIPTOR


@dataclass
class MyGameSession:
    context: object
    launch_options: GameLaunchOptions

    def run(self) -> GameExitResult:
        # Run pygame loop here.
        return GameExitResult(GameExitAction.GAME_LIBRARY)


class MyGame:
    @property
    def descriptor(self):
        return DESCRIPTOR

    def create_session(self, context, launch_options):
        return MyGameSession(context, launch_options)
```

Không gọi `pygame.quit()` hoặc `sys.exit()` trong flow bình thường. Trả `GameExitResult` để platform quyết định bước tiếp theo.

## 4. Launch Options

Nếu game cần cấu hình trước khi chạy, thêm method tùy chọn:

```python
def configure_launch(self, context):
    return GameLaunchOptions(mode="solo")
```

Platform sẽ gọi method này nếu tồn tại. Nếu trả `None`, launch bị hủy và platform quay về library.

## 5. Đăng Ký Registry

Thêm game vào `build_default_registry()` trong
`src/platform/bootstrap/composition.py`:

```python
registry.register(MyGame())
```

Home/library/app runtime không được import game cụ thể. Composition root là nơi
duy nhất của platform được import public game adapters như
`src.games.my_game.game.MyGame`.

## 6. Assets

Đặt asset runtime trong canonical root:

```text
assets/games/my_game/
  thumbnails/card.png
  images/foo.png
```

Dùng `context.assets.game("my_game", "images/foo.png")` để resolve asset game, hoặc khai báo `thumbnail=Path("games/my_game/thumbnails/card.png")` trong descriptor. Nếu asset thiếu, game nên dùng fallback UI hoặc `AssetService.image/scaled_image` thay vì crash.

## 7. Tests

Tối thiểu nên có:

- descriptor test;
- `create_session` test;
- lifecycle/result mapping test nếu có thể fake pygame;
- launch options test nếu game có cấu hình.

Architecture tests trong `tests/architecture` sẽ fail nếu platform import game
internals, game import game khác, domain import Pygame hoặc legacy root import
quay lại.
