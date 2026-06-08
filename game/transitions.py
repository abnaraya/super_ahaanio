"""Screen transition effects (fade in / fade out)."""
import pygame
from game.constants import WIDTH, HEIGHT


class TransitionManager:
    """Manages fade-in and fade-out transitions between game states."""

    def __init__(self):
        self._surface = pygame.Surface((WIDTH, HEIGHT))
        self._surface.fill((0, 0, 0))
        self._alpha = 0          # 0 = fully transparent, 255 = fully opaque
        self._direction = 0      # +1 = fading out (to black), -1 = fading in (from black)
        self._speed = 12         # alpha change per frame
        self.active = False
        self._callback = None    # called when fade-out completes

    def start_fade_out(self, on_complete=None):
        """Fade to black.  on_complete is called when fully black."""
        self._direction = 1
        self._alpha = 0
        self.active = True
        self._callback = on_complete

    def start_fade_in(self):
        """Fade from black to clear."""
        self._direction = -1
        self._alpha = 255
        self.active = True
        self._callback = None

    def update(self):
        if not self.active:
            return
        self._alpha += self._speed * self._direction
        if self._alpha >= 255:
            self._alpha = 255
            if self._callback:
                self._callback()
                self._callback = None
            # After fade-out completes, auto-start fade-in
            self.start_fade_in()
        elif self._alpha <= 0:
            self._alpha = 0
            self.active = False

    def draw(self, screen: pygame.Surface):
        if not self.active:
            return
        self._surface.set_alpha(int(self._alpha))
        screen.blit(self._surface, (0, 0))
