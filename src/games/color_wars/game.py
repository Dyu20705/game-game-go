"""Game Game Go adapter for the legacy Color Wars runtime."""

from dataclasses import dataclass

from src.platform.games import GameExitAction, GameExitResult, GameLaunchOptions

from .manifest import DESCRIPTOR

MODE_PVP = "pvp"
MODE_PVBOT = "pvbot"
DIFFICULTIES = ("easy", "medium", "hard")


class _PlatformMusicBridge:
    """Expose the legacy music API on top of the platform audio service."""

    def __init__(self, context):
        self._context = context

    def enter_menu(self):
        self._context.audio.play_menu_music()

    def enter_gameplay(self):
        self._context.audio.play_menu_music()

    def apply_audio_preferences(self, enabled, volume):
        self._context.settings.platform.sound_enabled = bool(enabled)
        self._context.settings.platform.set_master_volume(volume)
        self._context.audio.apply_preferences()


def _sync_legacy_settings_from_platform(context):
    from src.games.color_wars.runtime.settings import AppSettings

    platform_settings = context.settings.platform
    return AppSettings(
        sound_enabled=platform_settings.sound_enabled,
        sound_volume=platform_settings.master_volume,
        fullscreen=platform_settings.fullscreen,
        language=platform_settings.language,
    )


def _sync_platform_from_legacy(context, legacy_settings):
    context.settings.platform.sound_enabled = legacy_settings.sound_enabled
    context.settings.platform.set_master_volume(legacy_settings.sound_volume)
    context.settings.platform.fullscreen = legacy_settings.fullscreen
    context.settings.platform.language = legacy_settings.language
    context.localization.set_language(legacy_settings.language)


@dataclass
class ColorWarsSession:
    """Run one Color Wars match through the platform contract."""

    context: object
    launch_options: GameLaunchOptions

    def run(self) -> GameExitResult:
        from src.games.color_wars.runtime.loop import run_game

        legacy_settings = _sync_legacy_settings_from_platform(self.context)
        result = run_game(
            game_mode=self.launch_options.mode or MODE_PVBOT,
            difficulty=self.launch_options.difficulty or "easy",
            settings=legacy_settings,
            music=_PlatformMusicBridge(self.context),
        )
        _sync_platform_from_legacy(self.context, legacy_settings)
        if result is None:
            return GameExitResult(GameExitAction.QUIT)
        return GameExitResult(
            GameExitAction.GAME_LIBRARY,
            payload={
                "game_id": DESCRIPTOR.game_id,
                "mode": self.launch_options.mode or MODE_PVBOT,
                "difficulty": self.launch_options.difficulty or "easy",
                "legacy_result": result,
            },
        )


class ColorWarsGame:
    """Color Wars mini-game module."""

    @property
    def descriptor(self):
        return DESCRIPTOR

    def configure_launch(self, context) -> GameLaunchOptions | None:
        return run_color_wars_launch_scene(context)

    def create_session(self, context, launch_options: GameLaunchOptions) -> ColorWarsSession:
        mode = launch_options.mode if launch_options.mode in (MODE_PVP, MODE_PVBOT) else MODE_PVBOT
        difficulty = launch_options.difficulty if launch_options.difficulty in DIFFICULTIES else "easy"
        context.settings.update_game_settings(
            DESCRIPTOR.game_id,
            {
                "last_mode": mode,
                "last_difficulty": difficulty,
            },
        )
        return ColorWarsSession(
            context=context,
            launch_options=GameLaunchOptions(mode=mode, difficulty=difficulty, custom=launch_options.custom),
        )


def run_color_wars_launch_scene(context) -> GameLaunchOptions | None:
    """Collect Color Wars-specific launch options without leaking them into platform scenes."""

    import pygame

    screen = context.screen
    clock = context.clock
    saved = context.settings.get_game_settings(DESCRIPTOR.game_id)
    mode = str(saved.get("last_mode", MODE_PVBOT))
    difficulty = str(saved.get("last_difficulty", "easy"))
    if mode not in (MODE_PVP, MODE_PVBOT):
        mode = MODE_PVBOT
    if difficulty not in DIFFICULTIES:
        difficulty = "easy"

    title_font = pygame.font.SysFont("segoeui", 40, bold=True)
    body_font = pygame.font.SysFont("segoeui", 22)
    button_font = pygame.font.SysFont("segoeui", 20, bold=True)

    def button(rect, label, active=False):
        color = (78, 154, 118) if active else (48, 60, 70)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        pygame.draw.rect(screen, (230, 238, 244), rect, 1, border_radius=8)
        text = button_font.render(label, True, (242, 246, 250))
        screen.blit(text, text.get_rect(center=rect.center))

    while True:
        width, height = screen.get_size()
        back_rect = pygame.Rect(24, 24, 130, 44)
        pvp_rect = pygame.Rect(width // 2 - 230, 190, 210, 56)
        bot_rect = pygame.Rect(width // 2 + 20, 190, 210, 56)
        diff_rects = [pygame.Rect(width // 2 - 330 + index * 230, 290, 200, 56) for index in range(3)]
        start_rect = pygame.Rect(width // 2 - 150, height - 130, 300, 60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return None
                if pvp_rect.collidepoint(event.pos):
                    mode = MODE_PVP
                elif bot_rect.collidepoint(event.pos):
                    mode = MODE_PVBOT
                for rect, value in zip(diff_rects, DIFFICULTIES):
                    if rect.collidepoint(event.pos):
                        difficulty = value
                        mode = MODE_PVBOT
                if start_rect.collidepoint(event.pos):
                    return GameLaunchOptions(mode=mode, difficulty=difficulty)

        screen.fill((22, 28, 34))
        title = title_font.render("Color Wars", True, (242, 246, 250))
        screen.blit(title, title.get_rect(center=(width // 2, 92)))
        desc = body_font.render("Choose match type before launching the mini-game.", True, (179, 191, 201))
        screen.blit(desc, desc.get_rect(center=(width // 2, 135)))
        button(back_rect, context.localization.get("common.back"))
        button(pvp_rect, "PvP", mode == MODE_PVP)
        button(bot_rect, "PvBot", mode == MODE_PVBOT)
        for rect, value in zip(diff_rects, DIFFICULTIES):
            button(rect, value.title(), mode == MODE_PVBOT and difficulty == value)
        button(start_rect, context.localization.get("common.start"), True)
        pygame.display.flip()
        clock.tick(60)
