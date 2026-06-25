from __future__ import annotations

import pygame


class SoundManager:
    def __init__(self) -> None:
        self.enabled = True
        self.available = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.available = True
        except pygame.error:
            self.available = False

    def play(self, _name: str) -> None:
        if not self.enabled or not self.available:
            return

    def toggle(self) -> None:
        self.enabled = not self.enabled
