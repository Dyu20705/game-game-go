"""Reusable UI components for consistent rendering across scenes."""

import pygame


def _mix_color(base, delta):
    return tuple(max(0, min(255, c + delta)) for c in base)


def fit_surface(surface: pygame.Surface, max_width: int, max_height: int) -> pygame.Surface:
    """Scale a rendered surface down to fit bounds while preserving aspect ratio."""
    if max_width <= 0 or max_height <= 0:
        return pygame.Surface((1, 1), pygame.SRCALPHA)

    width = surface.get_width()
    height = surface.get_height()
    if width <= max_width and height <= max_height:
        return surface

    scale = min(max_width / max(1, width), max_height / max(1, height))
    target_w = max(1, int(width * scale))
    target_h = max(1, int(height * scale))
    return pygame.transform.smoothscale(surface, (target_w, target_h))


def blit_fitted_text(
    screen: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple,
    center: tuple,
    max_width: int,
    max_height: int,
):
    """Render and blit text centered, scaling down if it overflows."""
    rendered = font.render(text, True, color)
    fitted = fit_surface(rendered, max_width, max_height)
    screen.blit(fitted, fitted.get_rect(center=center))


def draw_interactive_button(
    screen: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    base_color: tuple,
    font: pygame.font.Font,
    text_color: tuple = (255, 255, 255),
    border_color: tuple = (255, 255, 255),
    border_radius: int = 12,
):
    """Draw a button with shared hover/pressed visual feedback and fitted label."""
    mouse_pos = pygame.mouse.get_pos()
    is_down = bool(pygame.mouse.get_pressed(num_buttons=3)[0])
    is_hovered = rect.collidepoint(mouse_pos)

    draw_rect = rect.copy()
    fill = base_color
    if is_hovered:
        fill = _mix_color(fill, 14)
    if is_hovered and is_down:
        fill = _mix_color(fill, -12)
        draw_rect.y += 1

    pygame.draw.rect(screen, fill, draw_rect, border_radius=border_radius)
    pygame.draw.rect(screen, border_color, draw_rect, 2, border_radius=border_radius)

    label_surface = font.render(label, True, text_color)
    fitted = fit_surface(label_surface, draw_rect.width - 14, draw_rect.height - 10)
    screen.blit(fitted, fitted.get_rect(center=draw_rect.center))


class Button:
    """Clickable button component with text and styling."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        bg_color: tuple,
        text_color: tuple,
        font: pygame.font.Font,
        border_radius: int = 8,
    ):
        """Initialize button.

        Args:
            rect: pygame.Rect for button position and size
            text: Button label text
            bg_color: RGB tuple for background color
            text_color: RGB tuple for text color
            font: pygame.font.Font for rendering text
            border_radius: Corner radius for rounded button
        """
        self.rect = rect
        self.text = text
        self.bg_color = bg_color
        self.text_color = text_color
        self.font = font
        self.border_radius = border_radius
        self.hovered = False

    def draw(self, screen: pygame.Surface):
        """Render button to screen.

        Args:
            screen: pygame display surface
        """
        pygame.draw.rect(
            screen,
            self.bg_color,
            self.rect,
            border_radius=self.border_radius,
        )

        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        """Check if button was clicked.

        Args:
            event: pygame MOUSEBUTTONDOWN event

        Returns:
            bool indicating if button was clicked
        """
        if event.type != pygame.MOUSEBUTTONDOWN:
            return False
        return self.rect.collidepoint(event.pos)

    def update_hover(self, mouse_pos: tuple):
        """Update hover state based on mouse position.

        Args:
            mouse_pos: (x, y) mouse position
        """
        self.hovered = self.rect.collidepoint(mouse_pos)


class Panel:
    """Rectangular container with background color and optional border."""

    def __init__(
        self,
        rect: pygame.Rect,
        bg_color: tuple,
        border_color: tuple | None = None,
        border_width: int = 0,
    ):
        """Initialize panel.

        Args:
            rect: pygame.Rect for panel position and size
            bg_color: RGB tuple for background color
            border_color: RGB tuple for border (None for no border)
            border_width: Width of border in pixels
        """
        self.rect = rect
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = border_width

    def draw(self, screen: pygame.Surface):
        """Render panel to screen.

        Args:
            screen: pygame display surface
        """
        pygame.draw.rect(screen, self.bg_color, self.rect)
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, self.rect, self.border_width)


class TextLabel:
    """Simple text label with positioning."""

    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color: tuple,
        position: tuple,
    ):
        """Initialize text label.

        Args:
            text: Text to display
            font: pygame.font.Font for rendering
            color: RGB tuple for text color
            position: (x, y) for top-left position
        """
        self.text = text
        self.font = font
        self.color = color
        self.position = position
        self.surface = font.render(text, True, color)
        self.rect = self.surface.get_rect(topleft=position)

    def draw(self, screen: pygame.Surface):
        """Render label to screen.

        Args:
            screen: pygame display surface
        """
        screen.blit(self.surface, self.rect)

    def set_text(self, text: str):
        """Update label text.

        Args:
            text: New text to display
        """
        self.text = text
        self.surface = self.font.render(text, True, self.color)
        self.rect = self.surface.get_rect(topleft=self.position)
