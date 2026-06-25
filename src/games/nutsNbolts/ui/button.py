from __future__ import annotations

from dataclasses import dataclass

import pygame

from . import theme


@dataclass
class Button:
    key: str
    label: str
    shortcut: str
    rect: pygame.Rect
    enabled: bool = True
    tooltip: str = ""
    hover_t: float = 0.0
    pressed: bool = False

    def update(self, mouse_pos: tuple[int, int], dt: float) -> None:
        target = 1.0 if self.enabled and self.rect.collidepoint(mouse_pos) else 0.0
        speed = 8.0
        self.hover_t += (target - self.hover_t) * min(1.0, dt * speed)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            self.pressed = False
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
            return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            was_pressed = self.pressed
            self.pressed = False
            return was_pressed and self.rect.collidepoint(event.pos)

        return False

    def draw(self, screen: pygame.Surface, fonts: dict[str, pygame.font.Font]) -> None:
        offset = 2 if self.pressed and self.enabled else 0
        rect = self.rect.move(0, offset)
        if not self.enabled:
            fill = theme.SURFACE_DARK
            border = theme.BORDER
            text_color = (124, 119, 108)
        else:
            bright = int(14 * self.hover_t)
            fill = theme.lighten(theme.SURFACE, bright)
            border = theme.darken(theme.BORDER, 20 if self.hover_t > 0.1 else 0)
            text_color = theme.TEXT

        shadow_rect = rect.move(0, 2)
        pygame.draw.rect(screen, (0, 0, 0, 26), shadow_rect, border_radius=8)
        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=8)

        label = fonts["button"].render(self.label, True, text_color)
        shortcut = fonts["tiny"].render(self.shortcut, True, theme.MUTED_TEXT)
        group_h = label.get_height() + shortcut.get_height() - 1
        y = rect.centery - group_h // 2
        screen.blit(label, label.get_rect(center=(rect.centerx, y + label.get_height() // 2)))
        screen.blit(
            shortcut,
            shortcut.get_rect(center=(rect.centerx, y + label.get_height() + shortcut.get_height() // 2)),
        )
