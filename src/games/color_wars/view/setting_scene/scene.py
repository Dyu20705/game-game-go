"""Setting scene and icon renderer."""

import pygame

from src.games.color_wars.view.commons import blit_fitted_text, draw_interactive_button, make_icon_surface


def draw_settings_icon(screen, rect, colors):
    """Draw settings icon using the shared icon style."""
    icon = make_icon_surface("settings", rect.size, bg_color=colors["btn_slate"])
    screen.blit(icon, rect.topleft)


def draw_setting_scene(screen, panel, fonts, colors, back_rect, back_icon, controls):
    """Draw settings scene content."""
    show_back = controls.get("show_back", True)

    shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    shade.fill((8, 16, 26, 150))
    screen.blit(shade, (0, 0))

    pygame.draw.rect(screen, (28, 39, 53), panel, border_radius=18)
    pygame.draw.rect(screen, (160, 185, 208), panel, 3, border_radius=18)

    if show_back and back_icon is not None and back_rect is not None:
        screen.blit(back_icon, back_rect.topleft)

    title_y = panel.y + int(panel.height * 0.12)
    section_y = panel.y + int(panel.height * 0.42)

    # Section backdrop to visually group sound controls.
    section_rect = pygame.Rect(panel.x + 28, section_y - 34, panel.width - 56, int(panel.height * 0.28))
    pygame.draw.rect(screen, (34, 48, 64), section_rect, border_radius=14)
    pygame.draw.rect(screen, (96, 124, 148), section_rect, 2, border_radius=14)
    blit_fitted_text(
        screen,
        fonts["main"],
        "Cài đặt trận đấu",
        (240, 247, 255),
        (panel.centerx, title_y),
        panel.width - 42,
        52,
    )

    checkbox_rect = controls["sound_checkbox"]
    slider_rect = controls["volume_slider"]
    knob_x = controls["volume_knob_x"]
    sound_enabled = controls["sound_enabled"]
    sound_volume = controls["sound_volume"]
    apply_btn = controls["apply_btn"]

    # Sound section heading and value are split to improve readability.
    sound_label_center = (slider_rect.centerx - 64, section_y - 6)
    value_label_center = (slider_rect.centerx + 78, section_y - 6)
    blit_fitted_text(
        screen,
        fonts["body"],
        "Âm thanh",
        (255, 255, 255),
        sound_label_center,
        slider_rect.width // 2,
        30,
    )
    blit_fitted_text(
        screen,
        fonts["body"],
        f"{int(sound_volume * 100)}%",
        (150, 206, 255),
        value_label_center,
        slider_rect.width // 3,
        30,
    )

    # Simple speaker glyph to make the sound section easier to scan.
    speaker_x = slider_rect.x - 20
    speaker_y = section_y - 16
    pygame.draw.polygon(
        screen,
        (220, 236, 249),
        [
            (speaker_x, speaker_y + 8),
            (speaker_x + 8, speaker_y + 8),
            (speaker_x + 14, speaker_y + 3),
            (speaker_x + 14, speaker_y + 21),
            (speaker_x + 8, speaker_y + 16),
            (speaker_x, speaker_y + 16),
        ],
    )
    pygame.draw.arc(screen, (150, 206, 255), (speaker_x + 12, speaker_y + 4, 12, 14), -1.0, 1.0, 2)

    pygame.draw.rect(screen, (230, 238, 246), checkbox_rect, border_radius=5)
    pygame.draw.rect(screen, (110, 136, 158), checkbox_rect, 2, border_radius=5)
    if sound_enabled:
        tick_points = [
            (checkbox_rect.x + 5, checkbox_rect.centery),
            (checkbox_rect.x + 10, checkbox_rect.bottom - 6),
            (checkbox_rect.right - 5, checkbox_rect.y + 6),
        ]
        pygame.draw.lines(screen, (75, 165, 98), False, tick_points, 3)

    pygame.draw.rect(screen, (120, 140, 160), slider_rect, border_radius=10)
    fill_w = max(1, knob_x - slider_rect.x)
    fill_rect = pygame.Rect(slider_rect.x, slider_rect.y, fill_w, slider_rect.height)
    pygame.draw.rect(screen, (90, 170, 255), fill_rect, border_radius=10)
    pygame.draw.circle(screen, (170, 216, 255), (knob_x, slider_rect.centery), 16)
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, slider_rect.centery), 14)
    pygame.draw.circle(screen, (90, 170, 255), (knob_x, slider_rect.centery), 10)

    draw_interactive_button(
        screen,
        apply_btn,
        "Áp dụng",
        (90, 170, 255),
        fonts["body"],
        border_radius=14,
    )
