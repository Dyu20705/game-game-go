"""Home scene renderer."""


def draw_home_scene(screen, panel, fonts, palette, rects):
    """Draw the home menu as 4 controls only (play/quit/tutorial/settings)."""

    rects["draw_button"](
        screen,
        rects["play_btn"],
        "BẮT ĐẦU",
        palette["btn_green"],
        fonts["button"],
    )
    rects["draw_button"](
        screen,
        rects["quit_btn"],
        "THOÁT",
        palette["btn_red"],
        fonts["button"],
    )
