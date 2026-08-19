"""
Hospital component responsible for hospital building rendering, emergency cross graphics,
and goal status indication.
"""

import math
# pyrefly: ignore [missing-import]
import pygame
import config
from grid import grid_to_screen


class Hospital:
    def __init__(self, position=config.HOSPITAL_POS):
        self.row, self.col = position
        self.x, self.y = grid_to_screen(self.row, self.col)
        self.size = config.CELL_SIZE
        self.pulse_timer = 0.0

        # Fonts
        self.font_tag = pygame.font.SysFont("Helvetica", 11, bold=True)
        self.font_h = pygame.font.SysFont("Helvetica", 14, bold=True)

    def update(self, dt):
        """Update subtle glow pulse effect for hospital goal area."""
        self.pulse_timer += dt * 3.0

    def draw(self, surface):
        """Renders the hospital building visual, red cross insignia, and arrival pad."""
        center_x, center_y = self.x, self.y

        # Glowing Pulse Target Perimeter
        pulse_r = int((self.size // 2 + 5) + math.sin(self.pulse_timer) * 3)
        pygame.draw.circle(surface, (255, 71, 87, 100), (center_x, center_y), pulse_r, 2)

        # Base Hospital Pad (White Medical Building Base)
        pad_rect = pygame.Rect(
            center_x - self.size // 2 + 1,
            center_y - self.size // 2 + 1,
            self.size - 2,
            self.size - 2,
        )
        pygame.draw.rect(surface, (245, 248, 255), pad_rect, border_radius=6)
        pygame.draw.rect(surface, config.ACCENT_RED, pad_rect, 2, border_radius=6)

        # Red Emergency Cross Graphic (Center of Building Roof)
        cross_l = 14
        cross_w = 4
        # Vertical arm
        pygame.draw.rect(
            surface,
            config.ACCENT_RED,
            (center_x - cross_w // 2, center_y - cross_l // 2, cross_w, cross_l),
        )
        # Horizontal arm
        pygame.draw.rect(
            surface,
            config.ACCENT_RED,
            (center_x - cross_l // 2, center_y - cross_w // 2, cross_l, cross_w),
        )

        # "HOSPITAL" Label Tag underneath
        lbl_rect = pygame.Rect(center_x - 32, center_y + self.size // 2 + 3, 64, 18)
        pygame.draw.rect(surface, config.PANEL_CARD_BG, lbl_rect, border_radius=4)
        pygame.draw.rect(surface, config.ACCENT_RED, lbl_rect, 1, border_radius=4)

        txt = self.font_tag.render("🏥 HOSPITAL", True, config.TEXT_COLOR)
        surface.blit(
            txt, (center_x - txt.get_width() // 2, center_y + self.size // 2 + 4)
        )

