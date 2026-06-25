from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from . import theme


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: tuple[int, int, int]

    def update(self, dt: float) -> bool:
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 45 * dt
        return self.life <= 0

    def draw(self, screen: pygame.Surface) -> None:
        if self.life <= 0:
            return
        radius = max(1, int(3 * min(1, self.life)))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)


class Celebration:
    def __init__(self) -> None:
        self.particles: list[Particle] = []
        self.random = random.Random(7)

    def burst(self, center: tuple[int, int]) -> None:
        self.particles.clear()
        for index in range(28):
            angle = (math.tau / 28) * index
            speed = self.random.uniform(70, 145)
            self.particles.append(
                Particle(
                    center[0],
                    center[1],
                    math.cos(angle) * speed,
                    math.sin(angle) * speed - 25,
                    self.random.uniform(0.5, 0.9),
                    self.random.choice([theme.SELECT, theme.SUCCESS, (255, 255, 255)]),
                )
            )

    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if not p.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        for particle in self.particles:
            particle.draw(screen)
