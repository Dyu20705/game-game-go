"""Platform settings scene."""

from src.platform.scenes.base import PlatformAction, SceneResult
from src.platform.ui import theme
from src.platform.ui.components import draw_button, draw_text


def run_settings_scene(pygame, context) -> SceneResult:
    """Run a small platform settings screen."""

    screen = context.screen
    clock = context.clock
    loc = context.localization
    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    body_font = pygame.font.SysFont("segoeui", 22)
    button_font = pygame.font.SysFont("segoeui", 20, bold=True)

    while True:
        back_rect = pygame.Rect(24, 24, 130, 44)
        mute_rect = pygame.Rect(screen.get_width() // 2 - 150, 210, 300, 52)
        down_rect = pygame.Rect(screen.get_width() // 2 - 150, 286, 136, 52)
        up_rect = pygame.Rect(screen.get_width() // 2 + 14, 286, 136, 52)
        lang_rect = pygame.Rect(screen.get_width() // 2 - 150, 362, 300, 52)

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
                if mute_rect.collidepoint(event.pos):
                    context.settings.platform.sound_enabled = not context.settings.platform.sound_enabled
                    context.audio.apply_preferences()
                elif down_rect.collidepoint(event.pos):
                    context.settings.platform.set_master_volume(context.settings.platform.master_volume - 0.1)
                    context.audio.apply_preferences()
                elif up_rect.collidepoint(event.pos):
                    context.settings.platform.set_master_volume(context.settings.platform.master_volume + 0.1)
                    context.audio.apply_preferences()
                elif lang_rect.collidepoint(event.pos):
                    next_lang = "en" if context.settings.platform.language == "vi" else "vi"
                    context.settings.platform.language = next_lang
                    context.localization.set_language(next_lang)

        screen.fill(theme.BG)
        draw_button(pygame, screen, back_rect, loc.get("common.back"), button_font, color=theme.PANEL_ALT)
        draw_text(pygame, screen, title_font, loc.get("platform.settings.title"), (screen.get_width() // 2, 92))
        sound = "ON" if context.settings.platform.sound_enabled else "OFF"
        draw_button(pygame, screen, mute_rect, f"{loc.get('platform.settings.sound')}: {sound}", button_font, color=theme.PANEL)
        draw_button(pygame, screen, down_rect, "- Volume", button_font, color=theme.PANEL_ALT)
        draw_button(pygame, screen, up_rect, "+ Volume", button_font, color=theme.PANEL_ALT)
        volume_text = f"{loc.get('platform.settings.volume')}: {context.settings.platform.master_volume:.1f}"
        draw_text(pygame, screen, body_font, volume_text, (screen.get_width() // 2, 455), theme.MUTED)
        draw_button(pygame, screen, lang_rect, f"{loc.get('platform.settings.language')}: {context.settings.platform.language}", button_font, color=theme.PANEL)
        if context.blockchain is not None:
            health = context.blockchain.health()
            status = f"Blockchain: {health.mode} | Sapphire: {health.sapphire.value} | ROFL: {health.rofl.value}"
            draw_text(pygame, screen, body_font, status, (screen.get_width() // 2, 510), theme.MUTED)
        pygame.display.flip()
        clock.tick(60)
