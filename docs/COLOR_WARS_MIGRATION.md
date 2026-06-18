# Color Wars Migration

Color Wars ban đầu là toàn bộ ứng dụng. Sau refactor, Game Game Go là platform, còn Color Wars là mini-game đầu tiên.

## Mapping

```text
src/controller.py                 -> src/games/color_wars/controller.py
src/engine/                       -> src/games/color_wars/engine/
src/ai/                           -> src/games/color_wars/ai/
src/game/                         -> src/games/color_wars/runtime/
src/view/                         -> src/games/color_wars/view/
new adapter                       -> src/games/color_wars/game.py
new manifest                      -> src/games/color_wars/manifest.py
```

Các module legacy vẫn còn ở path cũ để test cũ và import cũ tiếp tục hoạt động trong giai đoạn chuyển tiếp. Adapter platform đã gọi runtime mới ở `src.games.color_wars.runtime.loop`.

## Preserved Behavior

- Luật nước đi giữ nguyên.
- Explosion vẫn dùng BFS và threshold 4.
- PvP/PvBot giữ nguyên.
- AI easy/medium/hard giữ nguyên.
- HUD, tutorial, settings overlay, fullscreen và animation gameplay được giữ trong Color Wars runtime.
- `run_game()` không gọi `pygame.quit()`; session map kết quả về `GameExitResult`.

## Shared Extraction

Đã tách mới ở platform:

- game contract và registry;
- platform settings/save service;
- shared audio service;
- localization service cho text platform;
- asset resolver;
- platform home/library/settings/about scenes.

## Compatibility Shims And Debt

Compatibility hiện là giữ nguyên source path cũ thay vì xóa ngay. Điều này làm repo có một giai đoạn duplicate code giữa legacy path và package mới. Lý do là giảm rủi ro cho test cũ và tránh rewrite toàn bộ trong một bước.

Technical debt còn lại:

- chuyển test cũ sang `tests/games/color_wars` và import namespace mới;
- loại bỏ legacy `src/ai`, `src/engine`, `src/game`, `src/view`, `src/controller.py` sau khi migration test hoàn tất;
- migrate toàn bộ text Color Wars sang localization key;
- chuyển asset vật lý của Color Wars vào `src/games/color_wars/assets` hoặc package data;
- hợp nhất legacy `MusicManager` với `AudioService` sâu hơn.

