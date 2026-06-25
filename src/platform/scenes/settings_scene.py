"""Platform settings scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_settings_scene(pygame, context) -> SceneResult:
    """Run the platform settings panel."""

    screen = context.screen
    clock = context.clock
    title_font = pygame.font.SysFont("segoeui", 38, bold=True)
    section_font = pygame.font.SysFont("segoeui", 22, bold=True)
    body_font = pygame.font.SysFont("segoeui", 16)
    button_font = pygame.font.SysFont("segoeui", 18, bold=True)
    feedback = ""

    while True:
        context.audio.update()
        width, height = screen.get_size()
        panel = pygame.Rect(max(24, (width - 760) // 2), 72, min(760, width - 48), max(520, height - 144))
        back_rect = pygame.Rect(panel.x + 24, panel.y + 24, 120, 44)
        sound_card = pygame.Rect(panel.x + 28, panel.y + 94, panel.width - 56, 174)
        exp_card = pygame.Rect(panel.x + 28, sound_card.bottom + 18, panel.width - 56, 116)
        account_card = pygame.Rect(panel.x + 28, exp_card.bottom + 18, panel.width - 56, 96)

        music_rect = pygame.Rect(sound_card.x + 22, sound_card.y + 82, 122, 44)
        next_rect = pygame.Rect(music_rect.right + 12, music_rect.y, 132, 44)
        vol_down_rect = pygame.Rect(next_rect.right + 24, music_rect.y, 44, 44)
        vol_up_rect = pygame.Rect(vol_down_rect.right + 10, music_rect.y, 44, 44)
        sfx_rect = pygame.Rect(exp_card.x + 22, exp_card.y + 50, 190, 42)
        full_rect = pygame.Rect(sfx_rect.right + 12, sfx_rect.y, 150, 42)
        reset_rect = pygame.Rect(full_rect.right + 12, sfx_rect.y, 170, 42)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return SceneResult(PlatformAction.QUIT)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                context.save.save(context.settings.to_document())
                return SceneResult(PlatformAction.HOME)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    context.save.save(context.settings.to_document())
                    return SceneResult(PlatformAction.HOME)
                if music_rect.collidepoint(event.pos):
                    context.audio.toggle_music()
                    feedback = "Music paused" if not context.settings.platform.sound_enabled else "Music is back"
                elif next_rect.collidepoint(event.pos):
                    context.audio.next_track()
                    feedback = "Next song"
                elif vol_down_rect.collidepoint(event.pos):
                    context.settings.platform.set_master_volume(context.settings.platform.master_volume - 0.1)
                    context.audio.apply_preferences()
                    feedback = "Volume updated"
                elif vol_up_rect.collidepoint(event.pos):
                    context.settings.platform.set_master_volume(context.settings.platform.master_volume + 0.1)
                    context.audio.apply_preferences()
                    feedback = "Volume updated"
                elif sfx_rect.collidepoint(event.pos):
                    context.settings.platform.sound_enabled = not context.settings.platform.sound_enabled
                    context.audio.apply_preferences()
                    feedback = "Sound updated"
                elif full_rect.collidepoint(event.pos):
                    context.settings.platform.fullscreen = not context.settings.platform.fullscreen
                    feedback = "Restart may be needed"
                elif reset_rect.collidepoint(event.pos):
                    context.settings.platform.sound_enabled = True
                    context.settings.platform.master_volume = 0.8
                    context.audio.apply_preferences()
                    feedback = "Preferences reset"

        screen.fill(theme.BG)
        pygame.draw.rect(screen, theme.SIDEBAR, panel, border_radius=theme.RADIUS_XL)
        pygame.draw.rect(screen, theme.BORDER_SUBTLE, panel, 1, border_radius=theme.RADIUS_XL)
        draw_button(pygame, screen, back_rect, "Back", button_font, color=theme.PANEL_ALT)
        draw_text(pygame, screen, title_font, "Settings", (panel.centerx, panel.y + 48))

        _draw_card(pygame, screen, sound_card)
        screen.blit(section_font.render("Sound", True, theme.TEXT), (sound_card.x + 22, sound_card.y + 18))
        now = f"Now playing: {context.audio.current_track_title}"
        screen.blit(body_font.render(now, True, theme.MUTED), (sound_card.x + 22, sound_card.y + 52))
        music_label = "Pause" if context.settings.platform.sound_enabled else "Resume"
        draw_button(pygame, screen, music_rect, music_label, button_font, color=theme.BRAND_PRIMARY)
        draw_button(pygame, screen, next_rect, "Next song", button_font, color=theme.PANEL_ALT)
        draw_button(pygame, screen, vol_down_rect, "-", button_font, color=theme.PANEL_ALT)
        draw_button(pygame, screen, vol_up_rect, "+", button_font, color=theme.PANEL_ALT)
        volume = context.settings.platform.master_volume
        bar = pygame.Rect(sound_card.x + 22, sound_card.y + 142, sound_card.width - 44, 10)
        pygame.draw.rect(screen, theme.PANEL_ALT, bar, border_radius=theme.RADIUS_PILL)
        pygame.draw.rect(
            screen,
            theme.BRAND_PRIMARY,
            pygame.Rect(bar.x, bar.y, int(bar.width * volume), bar.height),
            border_radius=theme.RADIUS_PILL,
        )
        screen.blit(body_font.render(f"Volume {int(volume * 100)}%", True, theme.MUTED), (bar.x, bar.y - 24))

        _draw_card(pygame, screen, exp_card)
        screen.blit(section_font.render("Experience", True, theme.TEXT), (exp_card.x + 22, exp_card.y + 16))
        sound_label = "Sound effects: On" if context.settings.platform.sound_enabled else "Sound effects: Off"
        full_label = "Fullscreen: On" if context.settings.platform.fullscreen else "Fullscreen: Off"
        draw_button(pygame, screen, sfx_rect, sound_label, button_font, color=theme.PANEL_ALT)
        draw_button(pygame, screen, full_rect, full_label, button_font, color=theme.PANEL_ALT)
        draw_button(pygame, screen, reset_rect, "Reset prefs", button_font, color=theme.PANEL_ALT)

        _draw_card(pygame, screen, account_card)
        screen.blit(section_font.render("Account", True, theme.TEXT), (account_card.x + 22, account_card.y + 16))
        account = "Wallet disconnected"
        if context.blockchain is not None and context.blockchain.health().mode == "local":
            account = "Local guest profile"
        screen.blit(body_font.render(account, True, theme.MUTED), (account_card.x + 22, account_card.y + 54))
        if feedback:
            draw_text(pygame, screen, body_font, feedback, (panel.centerx, panel.bottom - 28), theme.BRAND_PRIMARY)

        pygame.display.flip()
        clock.tick(60)


def _draw_card(pygame, screen, rect):
    pygame.draw.rect(screen, theme.PANEL, rect, border_radius=theme.RADIUS_LG)
    pygame.draw.rect(screen, theme.BORDER_SUBTLE, rect, 1, border_radius=theme.RADIUS_LG)
