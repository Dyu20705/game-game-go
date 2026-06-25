from __future__ import annotations

from dataclasses import dataclass

import pygame

from src.platform.context import PlatformContext
from src.platform.games import GameExitAction, GameExitResult, GameLaunchOptions

from .animation import MoveAnimation, Pulse, Shake
from .level_generator import LevelGenerator
from .models import COLOR_NAMES, DIFFICULTIES, GameMode, Screw, StackState
from .rules import (
    can_move,
    is_completed_screw,
    is_victory,
    move_nut,
    restore_state,
)
from .sound import SoundManager
from .ui import theme
from .ui.button import Button
from .ui.effects import Celebration

GAME_ID = "nuts_and_bolts"
DEFAULT_DIFFICULTY = "normal"
VALID_DIFFICULTIES = tuple(DIFFICULTIES.keys())


@dataclass
class NutsAndBoltsSession:
    context: PlatformContext
    launch_options: GameLaunchOptions

    def __post_init__(self) -> None:
        self.screen = self.context.screen
        self.clock = self.context.clock
        self.fonts = {
            "title": theme.font(32, bold=True),
            "hud": theme.font(20, bold=True),
            "body": theme.font(18),
            "button": theme.font(16, bold=True),
            "small": theme.font(14),
            "tiny": theme.font(12),
        }

        self.generator = LevelGenerator()
        self.sound = SoundManager(self.context)
        self.celebration = Celebration()

        self.difficulty_key = self._initial_difficulty()
        self.screws: list[Screw] = []
        self.initial_state: StackState = ()
        self.history: list[tuple[int, int]] = []
        self.move_count = 0
        self.mode = GameMode.IDLE
        self.selected_index: int | None = None
        self.hovered_screw: int | None = None
        self.animation: MoveAnimation | None = None
        self.animation_is_undo = False
        self.shakes: dict[int, Shake] = {}
        self.pulses: dict[int, Pulse] = {}
        self.completed_indices: set[int] = set()
        self.status_message = "Select a screw."
        self.status_kind = "neutral"
        self.status_timer = 3.0
        self.win_alpha = 0.0
        self.completion_recorded = False
        self.modal_buttons: list[Button] = []
        self.buttons: dict[str, Button] = {}

        self.new_puzzle()

    @property
    def difficulty(self):
        return DIFFICULTIES[self.difficulty_key]

    def _initial_difficulty(self) -> str:
        launch_difficulty = self.launch_options.difficulty
        if launch_difficulty in VALID_DIFFICULTIES:
            return launch_difficulty

        settings = self.context.settings.get_game_settings(GAME_ID)
        preferred = settings.get("last_difficulty")
        if preferred in VALID_DIFFICULTIES:
            return str(preferred)
        return DEFAULT_DIFFICULTY

    def _game_settings(self) -> dict[str, object]:
        return self.context.settings.get_game_settings(GAME_ID)

    def apply_difficulty(self, difficulty_key: str) -> None:
        if difficulty_key not in VALID_DIFFICULTIES:
            difficulty_key = DEFAULT_DIFFICULTY
        self.difficulty_key = difficulty_key
        self.context.settings.update_game_settings(GAME_ID, {"last_difficulty": difficulty_key})
        self.new_puzzle()

    def build_exit_payload(self) -> dict[str, object]:
        return {
            "difficulty": self.difficulty_key,
            "moves": self.move_count,
            "completed": self.mode == GameMode.COMPLETED,
        }

    def exit_to_library(self) -> GameExitResult:
        return GameExitResult(GameExitAction.GAME_LIBRARY, self.build_exit_payload())

    def exit_to_quit(self) -> GameExitResult:
        return GameExitResult(GameExitAction.QUIT, self.build_exit_payload())

    def new_puzzle(self) -> None:
        level = self.generator.generate(self.difficulty)
        self.screws = level.screws
        self.initial_state = level.initial_state
        self.history.clear()
        self.move_count = 0
        self.selected_index = None
        self.animation = None
        self.animation_is_undo = False
        self.mode = GameMode.IDLE
        self.win_alpha = 0
        self.completion_recorded = False
        self.completed_indices = {i for i, screw in enumerate(self.screws) if is_completed_screw(screw)}
        self.show_status("New puzzle ready.", "success")

    def restart(self) -> None:
        restore_state(self.screws, self.initial_state)
        self.history.clear()
        self.move_count = 0
        self.selected_index = None
        self.animation = None
        self.animation_is_undo = False
        self.mode = GameMode.IDLE
        self.win_alpha = 0
        self.completion_recorded = False
        self.completed_indices = {i for i, screw in enumerate(self.screws) if is_completed_screw(screw)}
        self.show_status("Puzzle restarted.", "neutral")

    def show_status(self, message: str, kind: str = "neutral") -> None:
        self.status_message = message
        self.status_kind = kind
        self.status_timer = 2.4

    def cycle_difficulty(self) -> None:
        keys = list(DIFFICULTIES.keys())
        self.apply_difficulty(keys[(keys.index(self.difficulty_key) + 1) % len(keys)])

    def update_layout(self) -> None:
        width, height = self.screen.get_size()

        toolbar_y = height - 78
        button_w = min(126, max(100, (width - 120) // 5))
        button_h = 48
        gap = min(14, max(8, (width - button_w * 5 - 36) // 4))
        total_w = button_w * 5 + gap * 4
        start_x = width // 2 - total_w // 2
        specs = [
            ("back", "Library", "Esc"),
            ("undo", "Undo", "Z"),
            ("restart", "Restart", "R"),
            ("new", "New Puzzle", "Enter"),
            ("difficulty", "Difficulty", "1/2/3"),
        ]
        for index, (key, label, shortcut) in enumerate(specs):
            rect = pygame.Rect(start_x + index * (button_w + gap), toolbar_y, button_w, button_h)
            if key not in self.buttons:
                self.buttons[key] = Button(key, label, shortcut, rect)
            else:
                self.buttons[key].rect = rect
                self.buttons[key].label = label
                self.buttons[key].shortcut = shortcut

        self.buttons["undo"].enabled = bool(self.history) and self.mode not in {
            GameMode.MOVING,
            GameMode.COMPLETED,
        }
        self.buttons["back"].enabled = True
        for key in ("restart", "new", "difficulty"):
            self.buttons[key].enabled = self.mode != GameMode.MOVING

        modal_w = 420
        modal_x = width // 2 - modal_w // 2
        modal_y = height // 2 - 115
        self.modal_buttons = [
            Button("modal_back", "Library", "Esc", pygame.Rect(modal_x + 30, modal_y + 154, 108, 48)),
            Button("modal_new", "New Puzzle", "Enter", pygame.Rect(modal_x + 156, modal_y + 154, 116, 48)),
            Button("modal_restart", "Restart", "R", pygame.Rect(modal_x + 290, modal_y + 154, 100, 48)),
        ]

    def resize_surface(self, size: tuple[int, int]) -> None:
        width = max(int(size[0]), theme.MIN_SIZE[0])
        height = max(int(size[1]), theme.MIN_SIZE[1])
        fullscreen = bool(getattr(self.context.settings.platform, "fullscreen", False))
        flags = pygame.FULLSCREEN if fullscreen else pygame.RESIZABLE
        self.screen = pygame.display.set_mode((width, height), flags)
        self.context.screen = self.screen
        self.context.settings.platform.window_size = (width, height)

    def screw_positions(self) -> list[int]:
        width, _ = self.screen.get_size()
        count = len(self.screws)
        left = max(86, width // 2 - min(430, width // 2 - 70))
        right = min(width - 86, width // 2 + min(430, width // 2 - 70))
        if count <= 1:
            return [width // 2]
        gap = (right - left) / (count - 1)
        return [int(left + index * gap) for index in range(count)]

    def board_geometry(self) -> tuple[int, int, int]:
        _, height = self.screen.get_size()
        capacity = self.difficulty.capacity
        base_y = min(height - 142, 548)
        nut_gap = 46 if capacity <= 4 else 38
        top_y = base_y - nut_gap * capacity - 26
        return top_y, base_y, nut_gap

    def nut_position(self, screw_index: int, stack_index: int) -> tuple[float, float]:
        positions = self.screw_positions()
        _, base_y, nut_gap = self.board_geometry()
        return float(positions[screw_index]), float(base_y - 19 - stack_index * nut_gap)

    def destination_nut_position(self, destination_index: int) -> tuple[float, float]:
        stack_index = len(self.screws[destination_index].nuts)
        return self.nut_position(destination_index, stack_index)

    def update(self, dt: float) -> None:
        self.update_layout()
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos, dt)
        for button in self.modal_buttons:
            button.update(mouse_pos, dt)

        self.status_timer = max(0, self.status_timer - dt)
        for key in list(self.shakes.keys()):
            if self.shakes[key].update(dt):
                del self.shakes[key]
        for key in list(self.pulses.keys()):
            if self.pulses[key].update(dt):
                del self.pulses[key]

        if self.animation and self.animation.update(dt):
            self.finish_animation()

        if self.mode == GameMode.COMPLETED:
            self.win_alpha = min(1.0, self.win_alpha + dt * 3.4)
            self.celebration.update(dt)

        self.hovered_screw = self.hit_screw(mouse_pos)

    def finish_animation(self) -> None:
        if not self.animation:
            return

        source_index = self.animation.source_index
        destination_index = self.animation.destination_index
        move_nut(self.screws, source_index, destination_index)

        if self.animation_is_undo:
            self.move_count = max(0, self.move_count - 1)
            self.show_status("Move undone.", "neutral")
        else:
            self.history.append((source_index, destination_index))
            self.move_count += 1
            self.show_status("Select a screw.", "neutral")

        self.animation = None
        self.animation_is_undo = False
        self.selected_index = None
        self.update_completed_effects()

        if is_victory(self.screws):
            self.mode = GameMode.COMPLETED
            self.show_status("Puzzle complete!", "success")
            self.record_completion()
            w, h = self.screen.get_size()
            self.celebration.burst((w // 2, h // 2 - 82))
            self.sound.play("win")
        else:
            self.mode = GameMode.IDLE

    def record_completion(self) -> None:
        if self.completion_recorded:
            return
        self.completion_recorded = True

        settings = self._game_settings()
        raw_total = settings.get("total_completed", 0)
        total_completed = raw_total if isinstance(raw_total, int) and raw_total >= 0 else 0
        updates: dict[str, object] = {"total_completed": total_completed + 1}

        best_key = f"best_moves_{self.difficulty_key}"
        raw_best = settings.get(best_key)
        best_moves = raw_best if isinstance(raw_best, int) and raw_best > 0 else None
        if best_moves is None or self.move_count < best_moves:
            updates[best_key] = self.move_count

        self.context.settings.update_game_settings(GAME_ID, updates)

    def update_completed_effects(self) -> None:
        new_completed = {i for i, screw in enumerate(self.screws) if is_completed_screw(screw)}
        for index in new_completed - self.completed_indices:
            self.pulses[index] = Pulse()
            self.sound.play("complete")
        self.completed_indices = new_completed

    def hit_screw(self, mouse_pos: tuple[int, int]) -> int | None:
        top_y, base_y, _ = self.board_geometry()
        for index, x in enumerate(self.screw_positions()):
            rect = pygame.Rect(x - 52, top_y - 28, 104, base_y - top_y + 116)
            if rect.collidepoint(mouse_pos):
                return index
        return None

    def handle_event(self, event: pygame.event.Event) -> GameExitResult | None:
        if event.type == pygame.QUIT:
            return self.exit_to_quit()

        if event.type == pygame.VIDEORESIZE:
            self.resize_surface((event.w, event.h))
            return None

        if event.type == pygame.KEYDOWN:
            return self.handle_key(event.key)

        if self.mode == GameMode.COMPLETED:
            for button in self.modal_buttons:
                if button.handle_event(event):
                    return self.activate_button(button.key)
            return None

        for button in self.buttons.values():
            if button.handle_event(event):
                return self.activate_button(button.key)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.mode == GameMode.MOVING:
                return None
            screw_index = self.hit_screw(event.pos)
            if screw_index is not None:
                self.handle_screw_click(screw_index)
        return None

    def handle_key(self, key: int) -> GameExitResult | None:
        if key == pygame.K_ESCAPE:
            return self.exit_to_library()
        if self.mode == GameMode.MOVING:
            return None
        if key == pygame.K_RETURN:
            self.new_puzzle()
        elif key == pygame.K_z and self.mode != GameMode.COMPLETED:
            self.undo()
        elif key == pygame.K_r:
            self.restart()
        elif key == pygame.K_1:
            self.apply_difficulty("easy")
        elif key == pygame.K_2:
            self.apply_difficulty("normal")
        elif key == pygame.K_3:
            self.apply_difficulty("hard")
        elif key == pygame.K_m:
            self.sound.toggle()
        return None

    def activate_button(self, key: str) -> GameExitResult | None:
        if key in {"back", "modal_back"}:
            return self.exit_to_library()
        if key in {"new", "modal_new"}:
            self.new_puzzle()
        elif key in {"restart", "modal_restart"}:
            self.restart()
        elif key == "undo":
            self.undo()
        elif key == "difficulty":
            self.cycle_difficulty()
        return None

    def handle_screw_click(self, screw_index: int) -> None:
        screw = self.screws[screw_index]
        if self.mode == GameMode.IDLE:
            self.select_source(screw_index)
            return

        if self.mode != GameMode.SOURCE_SELECTED or self.selected_index is None:
            return

        if screw_index == self.selected_index:
            self.selected_index = None
            self.mode = GameMode.IDLE
            self.show_status("Move cancelled.", "neutral")
            return

        if screw.is_full():
            self.shakes[screw_index] = Shake()
            self.show_status("This screw is full.", "error")
            return

        if can_move(self.screws, self.selected_index, screw_index):
            self.start_move(self.selected_index, screw_index)
            return

        if not screw.is_empty() and not is_completed_screw(screw):
            self.select_source(screw_index)
        else:
            self.shakes[screw_index] = Shake()
            self.show_status("Invalid move.", "error")

    def select_source(self, screw_index: int) -> None:
        screw = self.screws[screw_index]
        if screw.is_empty():
            self.show_status("This screw is empty.", "error")
            self.shakes[screw_index] = Shake(amplitude=4)
            return
        if is_completed_screw(screw):
            self.show_status("This screw is already complete.", "neutral")
            return
        self.selected_index = screw_index
        self.mode = GameMode.SOURCE_SELECTED
        self.show_status("Select a destination.", "neutral")
        self.sound.play("select")

    def start_move(self, source_index: int, destination_index: int, *, undo: bool = False) -> None:
        nut_color = self.screws[source_index].top_nut()
        if nut_color is None:
            return
        start = self.nut_position(source_index, len(self.screws[source_index].nuts) - 1)
        end = self.destination_nut_position(destination_index)
        lift_y = min(start[1], end[1]) - 58
        self.animation = MoveAnimation(
            source_index,
            destination_index,
            nut_color,
            start,
            (start[0], lift_y),
            (end[0], lift_y),
            end,
        )
        self.animation_is_undo = undo
        self.mode = GameMode.MOVING
        self.selected_index = None
        self.sound.play("move")

    def undo(self) -> None:
        if self.mode in {GameMode.MOVING, GameMode.COMPLETED} or not self.history:
            return
        source_index, destination_index = self.history.pop()
        self.start_move(destination_index, source_index, undo=True)

    def draw(self) -> None:
        self.screen.fill(theme.BACKGROUND)
        self.draw_top_bar()
        self.draw_board()
        self.draw_status()
        self.draw_toolbar()
        if self.mode == GameMode.COMPLETED:
            self.draw_win_modal()
        pygame.display.flip()

    def draw_top_bar(self) -> None:
        width, _ = self.screen.get_size()
        rect = pygame.Rect(18, 16, width - 36, 64)
        pygame.draw.rect(self.screen, theme.SURFACE, rect, border_radius=10)
        pygame.draw.rect(self.screen, theme.BORDER, rect, width=1, border_radius=10)

        title = self.fonts["title"].render("NUTS & BOLTS", True, theme.TEXT)
        self.screen.blit(title, title.get_rect(midleft=(rect.left + 22, rect.centery)))

        hud = f"Moves: {self.move_count}    Difficulty: {self.difficulty.label}    Capacity: {self.difficulty.capacity}"
        hud_surface = self.fonts["hud"].render(hud, True, theme.TEXT)
        self.screen.blit(hud_surface, hud_surface.get_rect(midright=(rect.right - 22, rect.centery)))

    def draw_board(self) -> None:
        for index, screw in enumerate(self.screws):
            self.draw_screw(index, screw)
        if self.animation:
            x, y = self.animation.position()
            self.draw_nut((int(x), int(y)), self.animation.nut_color, lifted=True)

    def draw_screw(self, index: int, screw: Screw) -> None:
        positions = self.screw_positions()
        x = positions[index] + int(self.shakes[index].offset()) if index in self.shakes else positions[index]
        top_y, base_y, nut_gap = self.board_geometry()
        selected = self.selected_index == index
        hovered = self.hovered_screw == index and self.mode != GameMode.MOVING
        completed = is_completed_screw(screw)
        can_receive = self.mode == GameMode.SOURCE_SELECTED and self.selected_index != index and not screw.is_full()

        shadow = pygame.Surface((132, 42), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, theme.SHADOW, shadow.get_rect())
        self.screen.blit(shadow, (x - 66, base_y + 17))

        if selected:
            pygame.draw.circle(self.screen, theme.SELECT, (x, base_y + 4), 58, width=4)
        elif can_receive:
            pygame.draw.circle(self.screen, theme.VALID, (x, base_y + 4), 54, width=3)
        elif hovered:
            pygame.draw.circle(self.screen, theme.lighten(theme.BORDER, 20), (x, base_y + 4), 50, width=2)

        pygame.draw.line(self.screen, theme.METAL_DARK, (x + 4, top_y), (x + 4, base_y), width=13)
        pygame.draw.line(self.screen, theme.METAL, (x, top_y), (x, base_y), width=13)
        pygame.draw.line(self.screen, theme.METAL_LIGHT, (x - 3, top_y + 6), (x - 3, base_y - 6), width=4)
        pygame.draw.circle(self.screen, theme.METAL, (x, top_y), 12)
        pygame.draw.circle(self.screen, theme.METAL_LIGHT, (x - 3, top_y - 2), 4)
        pygame.draw.rect(self.screen, theme.METAL_DARK, pygame.Rect(x - 52, base_y, 104, 24), border_radius=8)
        pygame.draw.rect(self.screen, theme.METAL, pygame.Rect(x - 48, base_y - 2, 96, 22), border_radius=8)

        for stack_index, color in enumerate(screw.nuts):
            if self.animation and self.animation.source_index == index and stack_index == len(screw.nuts) - 1:
                continue
            y = base_y - 19 - stack_index * nut_gap
            lifted = selected and stack_index == len(screw.nuts) - 1
            if lifted:
                y -= 16
            self.draw_nut((x, y), color, lifted=lifted or hovered)

        self.draw_target_indicator(index, x, base_y + 36, screw, completed)

    def draw_target_indicator(self, index: int, x: int, y: int, screw: Screw, completed: bool) -> None:
        pulse = self.pulses[index].amount() if index in self.pulses else 0
        if screw.target_color is None:
            color = theme.SPARE
            label = "Spare"
        else:
            color = theme.PALETTE[screw.target_color]
            label = COLOR_NAMES[screw.target_color]
        rect = pygame.Rect(x - 43 - int(4 * pulse), y, 86 + int(8 * pulse), 16 + int(3 * pulse))
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, theme.darken(color, 35), rect, width=2, border_radius=8)
        if screw.target_color:
            self.draw_symbol(screw.target_color, (x, rect.centery), small=True)
        label_surface = self.fonts["small"].render(label, True, theme.TEXT)
        self.screen.blit(label_surface, label_surface.get_rect(center=(x, y + 35)))
        if completed:
            self.draw_check((x, y - 18), theme.SUCCESS)

    def draw_nut(self, center: tuple[int, int], color_key: str, *, lifted: bool = False) -> None:
        x, y = center
        if lifted:
            pygame.draw.ellipse(self.screen, (0, 0, 0, 36), pygame.Rect(x - 34, y + 18, 68, 13))
        color = theme.PALETTE[color_key]
        rect = pygame.Rect(x - 39, y - 15, 78, 30)
        pygame.draw.rect(self.screen, theme.darken(color, 42), rect.move(0, 5), border_radius=11)
        pygame.draw.rect(self.screen, color, rect, border_radius=11)
        pygame.draw.rect(self.screen, theme.lighten(color, 45), pygame.Rect(x - 29, y - 10, 58, 6), border_radius=4)
        hole = pygame.Rect(x - 14, y - 8, 28, 16)
        pygame.draw.ellipse(self.screen, theme.HOLE, hole)
        pygame.draw.ellipse(self.screen, theme.METAL_LIGHT, hole, width=2)
        self.draw_symbol(color_key, (x, y), small=False)

    def draw_symbol(self, color_key: str, center: tuple[int, int], *, small: bool) -> None:
        x, y = center
        color = (255, 255, 255) if not small else theme.TEXT
        scale = 0.75 if small else 1.0
        if color_key == "red":
            pygame.draw.circle(self.screen, color, (x + 25, y), int(4 * scale), width=2)
        elif color_key == "blue":
            pygame.draw.line(self.screen, color, (x + 20, y - 3), (x + 30, y - 3), width=2)
            pygame.draw.line(self.screen, color, (x + 20, y + 3), (x + 30, y + 3), width=2)
        elif color_key == "yellow":
            points = [(x + 25, y - 6), (x + 18, y + 5), (x + 32, y + 5)]
            pygame.draw.polygon(self.screen, color, points, width=2)
        elif color_key == "green":
            pygame.draw.rect(self.screen, color, pygame.Rect(x + 20, y - 5, 10, 10), width=2)
        elif color_key == "purple":
            points = [(x + 25, y - 7), (x + 32, y), (x + 25, y + 7), (x + 18, y)]
            pygame.draw.polygon(self.screen, color, points, width=2)
        elif color_key == "orange":
            pygame.draw.circle(self.screen, color, (x + 21, y), int(3 * scale))
            pygame.draw.circle(self.screen, color, (x + 30, y), int(3 * scale))

    def draw_check(self, center: tuple[int, int], color: tuple[int, int, int]) -> None:
        x, y = center
        pygame.draw.circle(self.screen, (255, 255, 255), center, 12)
        pygame.draw.circle(self.screen, color, center, 12, width=2)
        pygame.draw.lines(self.screen, color, False, [(x - 6, y), (x - 1, y + 5), (x + 7, y - 6)], width=3)

    def draw_status(self) -> None:
        if self.status_timer <= 0:
            return
        alpha = min(255, int(255 * min(1, self.status_timer / 0.45)))
        color = {
            "error": theme.ERROR,
            "success": theme.SUCCESS,
        }.get(self.status_kind, theme.MUTED_TEXT)
        surface = self.fonts["body"].render(self.status_message, True, color)
        surface.set_alpha(alpha)
        width, height = self.screen.get_size()
        self.screen.blit(surface, surface.get_rect(center=(width // 2, height - 112)))

    def draw_toolbar(self) -> None:
        width, height = self.screen.get_size()
        panel = pygame.Rect(18, height - 94, width - 36, 78)
        pygame.draw.rect(self.screen, theme.SURFACE, panel, border_radius=10)
        pygame.draw.rect(self.screen, theme.BORDER, panel, width=1, border_radius=10)
        for button in self.buttons.values():
            button.draw(self.screen, self.fonts)

    def draw_win_modal(self) -> None:
        width, height = self.screen.get_size()
        alpha = int(145 * self.win_alpha)
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((25, 24, 22, alpha))
        self.screen.blit(overlay, (0, 0))
        modal = pygame.Rect(width // 2 - 210, height // 2 - 115, 420, 230)
        pygame.draw.rect(self.screen, theme.SURFACE, modal, border_radius=16)
        pygame.draw.rect(self.screen, theme.SELECT, modal, width=3, border_radius=16)
        title = self.fonts["title"].render("PUZZLE COMPLETE!", True, theme.TEXT)
        moves = self.fonts["body"].render(f"Completed in {self.move_count} moves.", True, theme.TEXT)
        diff = self.fonts["small"].render(f"Difficulty: {self.difficulty.label}", True, theme.MUTED_TEXT)
        hint = self.fonts["small"].render("Press Enter or select New Puzzle to continue.", True, theme.MUTED_TEXT)
        self.screen.blit(title, title.get_rect(center=(modal.centerx, modal.y + 44)))
        self.screen.blit(moves, moves.get_rect(center=(modal.centerx, modal.y + 84)))
        self.screen.blit(diff, diff.get_rect(center=(modal.centerx, modal.y + 112)))
        self.screen.blit(hint, hint.get_rect(center=(modal.centerx, modal.y + 136)))
        for button in self.modal_buttons:
            button.draw(self.screen, self.fonts)
        self.celebration.draw(self.screen)

    def run(self) -> GameExitResult:
        while True:
            dt = self.clock.tick(theme.FPS) / 1000.0
            for event in pygame.event.get():
                result = self.handle_event(event)
                if result is not None:
                    return result
            self.update(dt)
            self.draw()
