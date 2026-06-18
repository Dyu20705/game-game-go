"""Main runtime loop: input, AI turn, and render."""

import pygame

from src.games.color_wars.ai import get_ai_move
from src.games.color_wars.controller import apply_move, get_scores
from src.games.color_wars.engine.rules import PLAYER_BLUE, PLAYER_RED
from src.games.color_wars.runtime.settings import AppSettings, clamp01
from src.games.color_wars.runtime.core import CoreSystems
from src.games.color_wars.runtime.state import GameState
from src.games.color_wars import view
from src.games.color_wars.view.commons import draw_tutorial_overlay, make_icon_surface
from src.games.color_wars.view.setting_scene import draw_setting_scene

MODE_PVP = "pvp"
MODE_PVBOT = "pvbot"
FPS = 60
EXPLOSION_ANIMATION_MS = 140


def run_game(game_mode=MODE_PVBOT, difficulty="easy", settings=None, music=None, core=None):
    """Run one match in pvp or pvbot mode."""
    if core is not None:
        if not isinstance(core, CoreSystems):
            raise TypeError("core must be CoreSystems")
        settings = core.settings
        music = core.music

    if game_mode not in (MODE_PVP, MODE_PVBOT):
        game_mode = MODE_PVBOT
    if difficulty not in ("easy", "medium", "hard", "ez", "med"):
        difficulty = "easy"
    if difficulty == "ez":
        difficulty = "easy"
    if difficulty == "med":
        difficulty = "medium"

    settings = settings or AppSettings()
    existing_surface = pygame.display.get_surface()
    if existing_surface is not None:
        settings.set_fullscreen(bool(existing_surface.get_flags() & pygame.FULLSCREEN))

    state = GameState()

    is_fullscreen = bool(settings.fullscreen)
    screen = view.drawScreen(fullscreen=is_fullscreen)
    clock = pygame.time.Clock()
    ui_icons = {
        "back": make_icon_surface("back", (40, 40), bg_color=(89, 114, 135)),
        "settings": make_icon_surface("settings", (40, 40), bg_color=(89, 114, 135)),
        "tutorial": make_icon_surface("tutorial", (40, 40), bg_color=(188, 140, 70)),
        "restart": make_icon_surface("restart", (72, 72), bg_color=(89, 114, 135)),
    }
    settings_open = False
    tutorial_open = False
    settings_dragging = False
    pending_sound_enabled = settings.sound_enabled
    pending_sound_volume = settings.sound_volume

    if music is not None:
        music.enter_gameplay()
        music.apply_audio_preferences(settings.sound_enabled, settings.sound_volume)

    running = True

    def get_corner_rects():
        width, _ = screen.get_size()
        return {
            "back": pygame.Rect(12, 10, 40, 40),
            "settings": pygame.Rect(width - 52, 10, 40, 40),
            "tutorial": pygame.Rect(width - 98, 10, 40, 40),
        }

    def get_settings_rects():
        width, height = screen.get_size()
        panel_w = min(560, width - 36)
        panel_h = min(360, height - 36)
        panel = pygame.Rect((width - panel_w) // 2, (height - panel_h) // 2, panel_w, panel_h)
        slider = pygame.Rect(panel.centerx - 170, panel.y + int(panel.height * 0.50), 300, 16)
        checkbox = pygame.Rect(slider.right + 16, slider.centery - 12, 24, 24)
        apply_btn = pygame.Rect(panel.centerx - 90, panel.bottom - int(panel.height * 0.17), 180, 40)
        knob_x = int(slider.x + slider.width * clamp01(pending_sound_volume))
        return {
            "panel": panel,
            "checkbox": checkbox,
            "slider": slider,
            "apply_btn": apply_btn,
            "knob_x": knob_x,
        }

    def draw_corner_icons():
        rects = get_corner_rects()
        screen.blit(ui_icons["back"], rects["back"].topleft)
        screen.blit(ui_icons["settings"], rects["settings"].topleft)
        screen.blit(ui_icons["tutorial"], rects["tutorial"].topleft)

    def draw_settings_overlay():
        rects = get_settings_rects()
        draw_setting_scene(
            screen,
            rects["panel"],
            {
                "main": pygame.font.SysFont("segoeui", max(26, int(screen.get_height() * 0.05)), bold=True),
                "body": pygame.font.SysFont("segoeui", max(17, int(screen.get_height() * 0.028))),
            },
            {
                "text_main": (240, 247, 255),
                "subtitle": (198, 216, 232),
                "btn_slate": (120, 140, 160),
                "btn_green": (75, 165, 98),
                "btn_blue": (72, 137, 196),
            },
            None,
            None,
            {
                "sound_checkbox": rects["checkbox"],
                "volume_slider": rects["slider"],
                "volume_knob_x": rects["knob_x"],
                "sound_enabled": pending_sound_enabled,
                "sound_volume": pending_sound_volume,
                "apply_btn": rects["apply_btn"],
                "show_back": False,
            },
        )

        return rects

    def play_explosion_animation(steps):
        nonlocal running, screen, is_fullscreen
        if not steps:
            return

        frames_per_step = max(4, int(FPS * EXPLOSION_ANIMATION_MS / 1000))
        for step in steps:
            for frame in range(frames_per_step):
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        return
                    if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                        screen = view.drawScreen(fullscreen=False, size=event.size)
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                        screen, is_fullscreen = view.toggle_fullscreen(is_fullscreen, screen)
                        settings.set_fullscreen(is_fullscreen)

                if not running:
                    return

                blue_score, red_score = get_scores(state)
                view.drawScene(
                    screen,
                    state,
                    state.board,
                    state.dots,
                    state.current_player,
                    blue_score,
                    red_score,
                    state.winner,
                    game_mode,
                    difficulty,
                )
                progress = (frame + 1) / frames_per_step
                layout = view.compute_layout(screen, state.grid_size)
                view.drawExplosionOverlay(screen, layout, step, progress)
                pygame.display.flip()
                clock.tick(FPS)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
                screen = view.drawScreen(fullscreen=False, size=event.size)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    state = GameState()
                elif event.key == pygame.K_m:
                    game_mode = MODE_PVP if game_mode == MODE_PVBOT else MODE_PVBOT
                    state = GameState()
                elif event.key == pygame.K_h:
                    tutorial_open = not tutorial_open
                elif event.key == pygame.K_F11:
                    screen, is_fullscreen = view.toggle_fullscreen(is_fullscreen, screen)
                    settings.set_fullscreen(is_fullscreen)
                elif event.key == pygame.K_ESCAPE:
                    if tutorial_open:
                        tutorial_open = False
                    elif state.winner is None and settings_open:
                        settings_open = False
                    else:
                        if music is not None:
                            music.enter_menu()
                        return "home"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos
                corner_rects = get_corner_rects()

                if state.winner is not None:
                    win_rects = view.get_win_action_rects(screen)
                    if win_rects["restart_rect"].collidepoint(mouse):
                        state = GameState()
                        settings_open = False
                        tutorial_open = False
                        if music is not None:
                            music.enter_gameplay()
                    elif win_rects["home_rect"].collidepoint(mouse):
                        if music is not None:
                            music.enter_menu()
                        return "home"
                    continue

                if corner_rects["back"].collidepoint(mouse):
                    if music is not None:
                        music.enter_menu()
                    return "home"
                if corner_rects["tutorial"].collidepoint(mouse):
                    tutorial_open = not tutorial_open
                    continue
                if corner_rects["settings"].collidepoint(mouse):
                    if not settings_open:
                        pending_sound_enabled = settings.sound_enabled
                        pending_sound_volume = settings.sound_volume
                    settings_open = not settings_open
                    continue

                if settings_open:
                    rects = get_settings_rects()
                    checkbox = rects["checkbox"]
                    slider = rects["slider"]
                    apply_btn = rects["apply_btn"]
                    knob_x = rects["knob_x"]
                    if apply_btn.collidepoint(mouse):
                        settings.set_sound_enabled(pending_sound_enabled)
                        settings.set_sound_volume(pending_sound_volume)
                        if music is not None:
                            music.apply_audio_preferences(settings.sound_enabled, settings.sound_volume)
                        settings_open = False
                    elif checkbox.collidepoint(mouse):
                        pending_sound_enabled = not pending_sound_enabled
                    elif slider.collidepoint(mouse):
                        settings_dragging = True
                        pending_sound_volume = clamp01((mouse[0] - slider.x) / max(1, slider.width))
                    elif abs(mouse[0] - knob_x) <= 18 and abs(mouse[1] - slider.centery) <= 18:
                        settings_dragging = True
                    continue

                if tutorial_open and "tutorial_overlay_rects" in locals():
                    close_rect = tutorial_overlay_rects.get("close_rect")
                    if close_rect and close_rect.collidepoint(mouse):
                        tutorial_open = False
                        continue

                if game_mode == MODE_PVP or state.current_player == PLAYER_BLUE:
                    row, col = view.get_cell_from_mouse(mouse, state.grid_size, screen)
                    explosion_steps = []
                    moved = apply_move(
                        state,
                        row,
                        col,
                        explosion_callback=explosion_steps.append,
                    )
                    if moved:
                        play_explosion_animation(explosion_steps)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                settings_dragging = False
            elif event.type == pygame.MOUSEMOTION and settings_dragging and settings_open:
                slider = get_settings_rects()["slider"]
                pending_sound_volume = clamp01((event.pos[0] - slider.x) / max(1, slider.width))

        if game_mode == MODE_PVBOT and state.winner is None and state.current_player == PLAYER_RED:
            move = get_ai_move(state.board, state.dots, difficulty)

            if move is None:
                blue_score, red_score = get_scores(state)
                if red_score == 0 and blue_score > 0:
                    state.winner = PLAYER_BLUE
                elif blue_score == 0 and red_score > 0:
                    state.winner = PLAYER_RED
                else:
                    state.current_player = PLAYER_BLUE
            else:
                explosion_steps = []
                moved = apply_move(
                    state,
                    move[0],
                    move[1],
                    player=PLAYER_RED,
                    explosion_callback=explosion_steps.append,
                )
                if moved:
                    play_explosion_animation(explosion_steps)

        blue_score, red_score = get_scores(state)
        view.drawScene(
            screen,
            state,
            state.board,
            state.dots,
            state.current_player,
            blue_score,
            red_score,
            state.winner,
            game_mode,
            difficulty,
        )

        draw_corner_icons()
        if settings_open and state.winner is None:
            draw_settings_overlay()

        tutorial_overlay_rects = {}
        if tutorial_open and state.winner is None:
            tutorial_lines = [
                "Giới thiệu: Color Wars là game chiến thuật theo lượt, mục tiêu là kiểm soát bàn cờ.",
                "Luật chơi: lượt đầu chỉ đặt vào ô trống, các lượt sau chỉ tăng quân ở ô thuộc về bạn.",
                "Nổ dây chuyền: ô có 4 chấm sẽ nổ và lan sang các ô kề bên, tạo combo liên tiếp.",
                "Mẹo chơi: giữ cạnh bàn cờ, tích lũy ô 3 chấm và tận dụng thời điểm để lật thế trận.",
                "Phím tắt: M đổi chế độ, R chơi lại, H mở hướng dẫn, F11 bật/tắt fullscreen, Esc quay lại.",
            ]
            tutorial_overlay_rects = draw_tutorial_overlay(
                screen,
                pygame.Rect(0, 0, screen.get_width(), screen.get_height()),
                {
                    "main": pygame.font.SysFont("segoeui", max(24, int(screen.get_height() * 0.05)), bold=True),
                    "body": pygame.font.SysFont("segoeui", max(15, int(screen.get_height() * 0.025))),
                },
                {
                    "text_main": (32, 45, 56),
                    "subtitle": (66, 80, 92),
                    "btn_blue": (72, 137, 196),
                    "btn_slate": (86, 111, 132),
                },
                tutorial_lines,
                close_label="Đóng",
            )

        if state.winner is not None:
            view.draw_win_scene(screen, state.winner, ui_icons)

        pygame.display.flip()
        clock.tick(FPS)

    return None


