"""Home menu scene for selecting mode and difficulty before a match."""

import pygame

from src.games.color_wars.runtime.settings import AppSettings, clamp01
from src.games.color_wars.runtime.core import CoreSystems
from src.games.color_wars.view.choose_diff_scene import draw_choose_diff_scene
from src.games.color_wars.view.choose_gamemode_scene import draw_choose_gamemode_scene
from src.games.color_wars.view.commons import draw_interactive_button, draw_tutorial_overlay, make_icon_surface
from src.games.color_wars.view.setting_scene import draw_setting_scene, draw_settings_icon

from ..window import drawScreen, toggle_fullscreen
from .assets import get_home_asset_path, load_icon_or_placeholder, load_image
from .scene import draw_home_scene

MENU = "menu"
CHOOSE_MODE = "choose_mode"
DIFFICULTY = "difficulty"
TUTORIAL = "tutorial"
SETTINGS = "settings"
MODE_PVP = "pvp"
MODE_PVBOT = "pvbot"

HOME_BG_FALLBACK = (26, 22, 24)
TITLE_COLOR = (247, 239, 224)
SUBTITLE_COLOR = (237, 228, 208)
PANEL_COLOR = (255, 248, 235, 50)
PANEL_BORDER = (232, 215, 186)
TEXT_MAIN = (248, 240, 223)
BTN_GREEN = (92, 162, 126)
BTN_AMBER = (214, 163, 85)
BTN_RED = (194, 95, 95)
BTN_BLUE = (112, 151, 202)
BTN_SLATE = (126, 121, 110)
DIFF_COLORS = {
    "easy": (72, 137, 196),
    "medium": (236, 172, 66),
    "hard": (213, 94, 89),
}


def difficulty_from_percent(percent):
    """Map slider percentage [0..1] to difficulty."""
    value = max(0.0, min(1.0, percent))
    if value < (1.0 / 3.0):
        return "easy"
    if value < (2.0 / 3.0):
        return "medium"
    return "hard"


def _difficulty_to_percent(difficulty):
    mapping = {"easy": 0.0, "medium": 0.5, "hard": 1.0}
    return mapping.get(difficulty, 0.0)


def _draw_button(screen, rect, label, color, font):
    draw_interactive_button(
        screen,
        rect,
        label,
        color,
        font,
        text_color=(255, 248, 235),
        border_color=(255, 248, 235),
        border_radius=max(12, rect.height // 4),
    )


def _draw_panel(screen, rect):
    panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surface, (18, 28, 44, 136), panel_surface.get_rect(), border_radius=24)
    pygame.draw.rect(panel_surface, (250, 236, 210, 125), panel_surface.get_rect(), 2, border_radius=24)
    soft_glow = pygame.Surface((rect.width, int(rect.height * 0.34)), pygame.SRCALPHA)
    soft_glow.fill((255, 252, 242, 24))
    panel_surface.blit(soft_glow, (0, 0))
    screen.blit(panel_surface, rect.topleft)


def compute_menu_icon_rects(panel):
    """Return tutorial and settings icon rects aligned inside the panel header."""
    icon_size = 40
    icon_gap = 8
    top_pad = 16
    right_pad = 18
    settings_icon_rect = pygame.Rect(panel.right - right_pad - icon_size, panel.y + top_pad, icon_size, icon_size)
    tutorial_icon_rect = pygame.Rect(settings_icon_rect.x - icon_gap - icon_size, panel.y + top_pad, icon_size, icon_size)
    return tutorial_icon_rect, settings_icon_rect


def _draw_background(screen, cache):
    size = screen.get_size()
    if cache.get("source") is None:
        for image_name in ("background.png", "bkgr.jpeg"):
            image_path = get_home_asset_path(image_name)
            try:
                cache["source"] = load_image(image_path, alpha=False)
                break
            except (pygame.error, FileNotFoundError, OSError):
                cache["source"] = None

    if cache.get("size") != size:
        composed = pygame.Surface(size)
        composed.fill(HOME_BG_FALLBACK)

        source = cache.get("source")
        if source is not None:
            src_w, src_h = source.get_size()

            scale = min(size[0] / src_w, size[1] / src_h)
            target_w = int(src_w * scale)
            target_h = int(src_h * scale)

            fitted = pygame.transform.smoothscale(source, (target_w, target_h))
            pos = ((size[0] - target_w) // 2, (size[1] - target_h) // 2)

            composed.blit(fitted, pos)

        vignette = pygame.Surface(size, pygame.SRCALPHA)
        vignette.fill((5, 4, 8, 70))
        pygame.draw.rect(vignette, (255, 245, 224, 26), pygame.Rect(0, 0, size[0], int(size[1] * 0.28)))
        composed.blit(vignette, (0, 0))

        cache["image"] = composed
        cache["size"] = size

    screen.blit(cache["image"], (0, 0))


def run_home_menu(settings=None, music=None, core=None):
    """Run home flow and return selected configuration or None when user exits."""
    if core is not None:
        if not isinstance(core, CoreSystems):
            raise TypeError("core must be CoreSystems")
        settings = core.settings
        music = core.music

    settings = settings or AppSettings()
    existing_surface = pygame.display.get_surface()
    if existing_surface is not None:
        settings.set_fullscreen(bool(existing_surface.get_flags() & pygame.FULLSCREEN))
    is_fullscreen = True
    settings.set_fullscreen(is_fullscreen)
    screen = drawScreen(fullscreen=is_fullscreen)

    clock = pygame.time.Clock()

    icon_size = (160, 160)
    icons = {
        "easy": load_icon_or_placeholder(get_home_asset_path("easy_icon.png"), icon_size, DIFF_COLORS["easy"]),
        "medium": load_icon_or_placeholder(get_home_asset_path("medium_icon.png"), icon_size, DIFF_COLORS["medium"]),
        "hard": load_icon_or_placeholder(get_home_asset_path("hard_icon.png"), icon_size, DIFF_COLORS["hard"]),
        "mode_pvp": load_icon_or_placeholder(get_home_asset_path("human.png"), (52, 52), BTN_BLUE),
        "mode_pvbot": load_icon_or_placeholder(get_home_asset_path("bot.png"), (52, 52), BTN_GREEN),
        "back": make_icon_surface("back", (42, 42), BTN_SLATE),
        "settings": make_icon_surface("settings", (42, 42), BTN_SLATE),
        "tutorial": make_icon_surface("tutorial", (42, 42), BTN_AMBER),
    }

    bg_cache = {}

    state = MENU
    selected_mode = MODE_PVBOT
    difficulty = "easy"
    slider_percent = _difficulty_to_percent(difficulty)
    dragging = False
    settings_return_state = MENU
    tutorial_open = False
    settings_dragging = False
    pending_sound_enabled = settings.sound_enabled
    pending_sound_volume = settings.sound_volume

    if music is not None:
        music.enter_menu()

    while True:
        width, height = screen.get_size()
        base = min(width, height)
        title_font = pygame.font.SysFont("segoeui", max(30, int(base * 0.078)), bold=True)
        main_font = pygame.font.SysFont("segoeui", max(22, int(base * 0.052)), bold=True)
        btn_font = pygame.font.SysFont("segoeui", max(18, int(base * 0.034)), bold=True)
        body_font = pygame.font.SysFont("segoeui", max(15, int(base * 0.026)))

        fonts = {
            "title": title_font,
            "main": main_font,
            "button": btn_font,
            "body": body_font,
        }

        panel_x = max(22, int(width * 0.05))
        panel_y = max(22, int(height * 0.05))
        panel_h = max(340, height - panel_y * 2)
        panel_ratio = min(0.48, width * 0.5 / 1920.0) if width >= 1280 else 0.52
        panel_w = max(320, min(int(width * panel_ratio), width - panel_x * 2 - 160))
        panel = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        back_rect = pygame.Rect(panel.x + 18, panel.y + 16, 46, 46)

        tutorial_icon_rect, settings_icon_rect = compute_menu_icon_rects(panel)

        center_x = panel.centerx
        menu_btn_h = max(60, int(panel.height * 0.13))
        menu_btn_w = min(int(panel.width * 0.76), max(240, int(width * 0.30)))
        menu_start_y = panel.y + int(panel.height * 0.42)

        play_btn = pygame.Rect(center_x - menu_btn_w // 2, menu_start_y, menu_btn_w, menu_btn_h)
        quit_btn = pygame.Rect(
            center_x - menu_btn_w // 2,
            menu_start_y + menu_btn_h + max(16, int(panel.height * 0.03)),
            menu_btn_w,
            menu_btn_h,
        )

        mode_btn_h = max(46, int(panel.height * 0.085))
        mode_btn_gap = max(10, int(panel.height * 0.015))
        pvp_btn = pygame.Rect(center_x - menu_btn_w // 2, panel.y + int(panel.height * 0.45), menu_btn_w, mode_btn_h)
        pvbot_btn = pygame.Rect(center_x - menu_btn_w // 2, panel.y + int(panel.height * 0.45) + mode_btn_h + mode_btn_gap, menu_btn_w, mode_btn_h)

        slider_rect = pygame.Rect(center_x - min(180, panel.width // 3), panel.y + int(panel.height * 0.58), min(360, panel.width * 2 // 3), 22)
        knob_x = int(slider_rect.x + slider_rect.width * slider_percent)
        play_match_btn = pygame.Rect(
            center_x - menu_btn_w // 2,
            panel.bottom - menu_btn_h - max(20, int(panel.height * 0.04)),
            menu_btn_w,
            menu_btn_h,
        )

        settings_w = min(560, width - 36)
        settings_h = min(360, height - 36)
        settings_panel = pygame.Rect((width - settings_w) // 2, (height - settings_h) // 2, settings_w, settings_h)
        settings_back_rect = pygame.Rect(settings_panel.x + 16, settings_panel.y + 16, 42, 42)
        settings_slider_w = min(300, settings_panel.width - 190)
        settings_volume_slider = pygame.Rect(
            settings_panel.centerx - settings_slider_w // 2,
            settings_panel.y + int(settings_panel.height * 0.50),
            settings_slider_w,
            16,
        )
        settings_sound_checkbox = pygame.Rect(settings_volume_slider.right + 16, settings_volume_slider.centery - 12, 24, 24)
        settings_apply_btn = pygame.Rect(settings_panel.centerx - 90, settings_panel.bottom - int(settings_panel.height * 0.17), 180, 40)
        settings_volume_knob_x = int(settings_volume_slider.x + settings_volume_slider.width * pending_sound_volume)

        tutorial_lines = [
            "Giới thiệu: Color Wars là game chiến thuật theo lượt, mục tiêu là chiếm nhiều ô hơn đối thủ.",
            "Luật chơi: lượt đầu chỉ đặt vào ô trống; các lượt sau chỉ được tăng quân ở ô bạn đang sở hữu.",
            "Nổ dây chuyền: ô đạt 4 chấm sẽ nổ, lan sang ô kề bên và có thể kích hoạt chuỗi nổ liên tiếp.",
            "Mẹo chơi: ưu tiên kiểm soát cạnh bàn cờ, tích lũy ô 3 chấm và chờ thời điểm tạo combo lớn.",
            "Phím tắt: Chuột trái để đi, M đổi chế độ, R chơi lại, H mở hướng dẫn, F11 bật/tắt fullscreen, Esc quay lại.",
        ]

        palette = {
            "title": TITLE_COLOR,
            "subtitle": SUBTITLE_COLOR,
            "text_main": TEXT_MAIN,
            "btn_green": BTN_GREEN,
            "btn_amber": BTN_AMBER,
            "btn_red": BTN_RED,
            "btn_blue": BTN_BLUE,
            "btn_slate": BTN_SLATE,
            "diff_colors": DIFF_COLORS,
        }

        shared_rects = {
            "draw_button": _draw_button,
            "back_rect": back_rect,
            "play_btn": play_btn,
            "quit_btn": quit_btn,
            "pvp_btn": pvp_btn,
            "pvbot_btn": pvbot_btn,
            "slider_rect": slider_rect,
            "knob_x": knob_x,
            "play_match_btn": play_match_btn,
            "settings_icon_rect": settings_icon_rect,
            "tutorial_icon_rect": tutorial_icon_rect,
            "settings_icon": icons["settings"],
            "tutorial_icon": icons["tutorial"],
            "sound_checkbox": settings_sound_checkbox,
            "volume_slider": settings_volume_slider,
            "volume_knob_x": settings_volume_knob_x,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None

            if event.type == pygame.VIDEORESIZE and not is_fullscreen:
                pass

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen, is_fullscreen = toggle_fullscreen(is_fullscreen, screen)
                    settings.set_fullscreen(is_fullscreen)
                elif event.key == pygame.K_h:
                    tutorial_open = not tutorial_open
                elif event.key == pygame.K_ESCAPE:
                    if tutorial_open:
                        tutorial_open = False
                    elif state == MENU:
                        return None
                    if state in (CHOOSE_MODE, TUTORIAL):
                        state = MENU
                    elif state == DIFFICULTY:
                        state = CHOOSE_MODE
                    elif state == SETTINGS:
                        state = settings_return_state

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = event.pos
                if state == MENU:
                    if tutorial_open:
                        pass
                    elif play_btn.collidepoint(mouse):
                        state = CHOOSE_MODE
                    elif tutorial_icon_rect.collidepoint(mouse):
                        tutorial_open = True
                    elif settings_icon_rect.collidepoint(mouse):
                        settings_return_state = MENU
                        pending_sound_enabled = settings.sound_enabled
                        pending_sound_volume = settings.sound_volume
                        state = SETTINGS
                    elif quit_btn.collidepoint(mouse):
                        return None

                elif state == CHOOSE_MODE:
                    if tutorial_open:
                        pass
                    elif back_rect.collidepoint(mouse):
                        state = MENU
                    elif tutorial_icon_rect.collidepoint(mouse):
                        tutorial_open = True
                    elif settings_icon_rect.collidepoint(mouse):
                        settings_return_state = CHOOSE_MODE
                        pending_sound_enabled = settings.sound_enabled
                        pending_sound_volume = settings.sound_volume
                        state = SETTINGS
                    elif pvp_btn.collidepoint(mouse):
                        selected_mode = MODE_PVP
                        difficulty = "easy"
                        return {
                            "game_mode": selected_mode,
                            "difficulty": difficulty,
                        }
                    elif pvbot_btn.collidepoint(mouse):
                        selected_mode = MODE_PVBOT
                        state = DIFFICULTY

                elif state == DIFFICULTY:
                    if tutorial_open:
                        pass
                    elif back_rect.collidepoint(mouse):
                        state = CHOOSE_MODE
                    elif tutorial_icon_rect.collidepoint(mouse):
                        tutorial_open = True
                    elif settings_icon_rect.collidepoint(mouse):
                        settings_return_state = DIFFICULTY
                        pending_sound_enabled = settings.sound_enabled
                        pending_sound_volume = settings.sound_volume
                        state = SETTINGS
                    elif play_match_btn.collidepoint(mouse):
                        return {
                            "game_mode": selected_mode,
                            "difficulty": difficulty,
                        }
                    elif slider_rect.collidepoint(mouse):
                        dragging = True
                        slider_percent = (mouse[0] - slider_rect.x) / max(1, slider_rect.width)
                        difficulty = difficulty_from_percent(slider_percent)
                    elif abs(mouse[0] - knob_x) <= 24 and abs(mouse[1] - slider_rect.centery) <= 24:
                        dragging = True

                elif state == TUTORIAL:
                    if back_rect.collidepoint(mouse):
                        state = MENU
                    elif settings_icon_rect.collidepoint(mouse):
                        settings_return_state = TUTORIAL
                        state = SETTINGS

                elif state == SETTINGS:
                    if tutorial_open:
                        tutorial_open = False
                        continue
                    if settings_back_rect.collidepoint(mouse):
                        state = settings_return_state
                    elif settings_apply_btn.collidepoint(mouse):
                        settings.set_sound_enabled(pending_sound_enabled)
                        settings.set_sound_volume(pending_sound_volume)
                        if music is not None:
                            music.apply_audio_preferences(settings.sound_enabled, settings.sound_volume)
                        state = settings_return_state
                    elif settings_sound_checkbox.collidepoint(mouse):
                        pending_sound_enabled = not pending_sound_enabled
                    elif settings_volume_slider.collidepoint(mouse):
                        settings_dragging = True
                        pending_sound_volume = clamp01((mouse[0] - settings_volume_slider.x) / max(1, settings_volume_slider.width))
                    elif abs(mouse[0] - settings_volume_knob_x) <= 20 and abs(mouse[1] - settings_volume_slider.centery) <= 20:
                        settings_dragging = True

                if tutorial_open:
                    close_rect = tutorial_overlay_rects.get("close_rect") if "tutorial_overlay_rects" in locals() else None
                    if close_rect is not None and close_rect.collidepoint(mouse):
                        tutorial_open = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                settings_dragging = False

            if event.type == pygame.MOUSEMOTION and dragging and state == DIFFICULTY:
                slider_percent = (event.pos[0] - slider_rect.x) / max(1, slider_rect.width)
                difficulty = difficulty_from_percent(slider_percent)

            if event.type == pygame.MOUSEMOTION and settings_dragging and state == SETTINGS:
                pending_sound_volume = clamp01((event.pos[0] - settings_volume_slider.x) / max(1, settings_volume_slider.width))

        slider_percent = max(0.0, min(1.0, slider_percent))
        pending_sound_volume = clamp01(pending_sound_volume)
        if not dragging:
            slider_percent = _difficulty_to_percent(difficulty)

        _draw_background(screen, bg_cache)
        _draw_panel(screen, panel)

        if state == MENU:
            screen.blit(icons["tutorial"], tutorial_icon_rect.topleft)
            screen.blit(icons["settings"], settings_icon_rect.topleft)
            draw_home_scene(screen, panel, fonts, palette, shared_rects)

        elif state == CHOOSE_MODE:
            screen.blit(icons["tutorial"], tutorial_icon_rect.topleft)
            draw_choose_gamemode_scene(
                screen,
                panel,
                {"main": main_font, "button": btn_font},
                palette,
                shared_rects,
                icons,
            )

        elif state == DIFFICULTY:
            screen.blit(icons["tutorial"], tutorial_icon_rect.topleft)
            shared_rects["knob_x"] = int(slider_rect.x + slider_rect.width * slider_percent)
            draw_choose_diff_scene(
                screen,
                panel,
                {"main": main_font, "body": body_font, "button": btn_font},
                palette,
                shared_rects,
                difficulty,
                icons,
            )

        elif state == TUTORIAL:
            draw_settings_icon(screen, settings_icon_rect, palette)
            screen.blit(icons["tutorial"], tutorial_icon_rect.topleft)
        else:
            draw_setting_scene(
                screen,
                settings_panel,
                {"main": main_font, "body": body_font},
                palette,
                settings_back_rect,
                icons["back"],
                {
                    "sound_checkbox": settings_sound_checkbox,
                    "volume_slider": settings_volume_slider,
                    "volume_knob_x": int(settings_volume_slider.x + settings_volume_slider.width * pending_sound_volume),
                    "sound_enabled": pending_sound_enabled,
                    "sound_volume": pending_sound_volume,
                    "apply_btn": settings_apply_btn,
                    "show_back": True,
                },
            )

        tutorial_overlay_rects = {}
        if tutorial_open:
            tutorial_overlay_rects = draw_tutorial_overlay(
                screen,
                panel,
                {"main": main_font, "body": body_font},
                palette,
                tutorial_lines,
                close_label="Đóng",
            )

        pygame.display.flip()
        clock.tick(60)


