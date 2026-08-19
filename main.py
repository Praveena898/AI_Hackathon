"""
Main entry point for Emergency Response Ambulance Simulation Pygame Application.
"""

import sys
# pyrefly: ignore [missing-import]
import pygame
import config
from simulation import Simulation


def main():
    pygame.init()
    pygame.display.set_caption("Emergency Response Ambulance Simulation")

    # Set window icon (procedural surface)
    icon_surface = pygame.Surface((32, 32))
    icon_surface.fill(config.BG_DARK)
    pygame.draw.rect(icon_surface, (250, 250, 255), (4, 4, 24, 24), border_radius=4)
    pygame.draw.rect(icon_surface, config.ACCENT_RED, (13, 8, 6, 16))
    pygame.draw.rect(icon_surface, config.ACCENT_RED, (8, 13, 16, 6))
    pygame.display.set_icon(icon_surface)

    # Initialize Screen & Clock
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    simulation = Simulation()

    running = True
    while running:
        # Delta time in seconds
        dt = clock.tick(config.FPS) / 1000.0
        dt = min(dt, 0.1)  # Clamp delta time to prevent large leaps on window drag

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                simulation.handle_event(event)

        # Update Logic
        simulation.update(dt)

        # Draw Frame
        simulation.draw(screen)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
