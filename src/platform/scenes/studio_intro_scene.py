"""Chillody Studio intro shown once per application launch."""

from __future__ import annotations

from src.platform.ui import theme

INTRO_FADE_IN_MS = 520
INTRO_HOLD_MS = 1150
INTRO_FADE_OUT_MS = 520
INTRO_TOTAL_MS = INTRO_FADE_IN_MS + INTRO_HOLD_MS + INTRO_FADE_OUT_MS


def run_studio_intro_scene(pygame, context, *, duration_ms: int = INTRO_TOTAL_MS) -> None:
    """Render a short skippable studio intro without changing app navigation."""

    screen = context.screen
    clock = context.clock
    logo = context.assets.image(pygame, context.assets.branding("studio_logo_runtime.png"), fallback_size=(320, 320))
    caption_font = context.assets.font(pygame, "display", 24, bold=True)
    hint_font = context.assets.font(pygame, "body", 13)
    start = pygame.time.get_ticks()
    duration_ms = max(250, int(duration_ms))

    while True:
        elapsed = pygame.time.get_ticks() - start
        if elapsed >= duration_ms:
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.event.post(event)
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                return
            if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE,
                pygame.K_RETURN,
                pygame.K_SPACE,
                pygame.K_KP_ENTER,
            ):
                return

        context.audio.update()
        width, height = screen.get_size()
        screen.fill((252, 244, 248))
        _draw_soft_intro_background(pygame, screen, width, height)

        alpha = _intro_alpha(elapsed, duration_ms)
        logo_size = min(int(min(width, height) * 0.48), 340)
        scaled_logo = pygame.transform.smoothscale(logo, (logo_size, logo_size))
        scaled_logo.set_alpha(alpha)
        screen.blit(scaled_logo, scaled_logo.get_rect(center=(width // 2, int(height * 0.46))))

        caption = caption_font.render("Chillody Studio", True, (166, 104, 126))
        caption.set_alpha(alpha)
        screen.blit(caption, caption.get_rect(center=(width // 2, int(height * 0.75))))
        if elapsed > 700:
            hint = hint_font.render("Press Space, Enter, Esc or click to skip", True, (174, 135, 150))
            hint.set_alpha(min(170, int((elapsed - 700) / 300 * 170)))
            screen.blit(hint, hint.get_rect(center=(width // 2, height - 44)))

        pygame.display.flip()
        clock.tick(60)


def _intro_alpha(elapsed: int, duration_ms: int) -> int:
    fade_out_start = max(INTRO_FADE_IN_MS, duration_ms - INTRO_FADE_OUT_MS)
    if elapsed < INTRO_FADE_IN_MS:
        return int(255 * _ease_out(elapsed / INTRO_FADE_IN_MS))
    if elapsed >= fade_out_start:
        return int(255 * (1.0 - _ease_out((elapsed - fade_out_start) / max(1, duration_ms - fade_out_start))))
    return 255


def _ease_out(value: float) -> float:
    value = min(1.0, max(0.0, value))
    return 1.0 - (1.0 - value) ** 3


def _draw_soft_intro_background(pygame, screen, width: int, height: int) -> None:
    radius = max(width, height) // 3
    pygame.draw.circle(screen, (255, 232, 240), (int(width * 0.18), int(height * 0.25)), radius)
    pygame.draw.circle(screen, (238, 248, 255), (int(width * 0.82), int(height * 0.2)), radius)
    pygame.draw.circle(screen, (255, 246, 250), (int(width * 0.52), int(height * 0.82)), radius)
    pygame.draw.rect(screen, theme.BORDER_SUBTLE, screen.get_rect(), 1)
