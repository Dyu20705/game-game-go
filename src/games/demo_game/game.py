"""A tiny interactive mini-game proving the platform can launch multiple games."""

from dataclasses import dataclass
import random

from src.platform.games import GameExitAction, GameExitResult, GameLaunchOptions

from .manifest import DESCRIPTOR


@dataclass
class DemoGameSession:
    """Click Sprint session."""

    context: object
    launch_options: GameLaunchOptions
    duration_ms: int = 10000

    def run(self) -> GameExitResult:
        import pygame

        screen = self.context.screen
        clock = self.context.clock
        font = pygame.font.SysFont("segoeui", 26, bold=True)
        small = pygame.font.SysFont("segoeui", 18)
        started = pygame.time.get_ticks()
        score = 0
        radius = 26
        target = self._random_target(screen, radius)

        while True:
            now = pygame.time.get_ticks()
            remaining = max(0, self.duration_ms - (now - started))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return GameExitResult(GameExitAction.QUIT, {"score": score})
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return GameExitResult(GameExitAction.GAME_LIBRARY, {"score": score})
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    dx = event.pos[0] - target[0]
                    dy = event.pos[1] - target[1]
                    if dx * dx + dy * dy <= radius * radius:
                        score += 1
                        target = self._random_target(screen, radius)

            if remaining <= 0:
                return GameExitResult(GameExitAction.GAME_LIBRARY, {"score": score})

            screen.fill((18, 24, 30))
            pygame.draw.circle(screen, (230, 96, 93), target, radius)
            score_text = font.render(f"Score: {score}", True, (242, 246, 250))
            time_text = small.render(f"{remaining / 1000:.1f}s  |  Esc: Library", True, (179, 191, 201))
            screen.blit(score_text, (28, 24))
            screen.blit(time_text, (28, 62))
            pygame.display.flip()
            clock.tick(60)

    @staticmethod
    def _random_target(screen, radius: int):
        width, height = screen.get_size()
        return (
            random.randint(radius + 20, max(radius + 20, width - radius - 20)),
            random.randint(110, max(110, height - radius - 20)),
        )


class DemoGame:
    """Click Sprint demo game module."""

    @property
    def descriptor(self):
        return DESCRIPTOR

    def create_session(self, context, launch_options: GameLaunchOptions) -> DemoGameSession:
        return DemoGameSession(context=context, launch_options=launch_options)

