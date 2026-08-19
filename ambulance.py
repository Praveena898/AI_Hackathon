"""
Ambulance vehicle component with vector graphic rendering, dynamic siren animation,
orientation facing, and smooth delta-time interpolation between grid waypoints.
"""

import math
import pygame
import config
from grid import grid_to_screen, screen_to_grid


class Ambulance:
    def __init__(self, start_pos=config.START_POS):
        self.start_row, self.start_col = start_pos
        self.row, self.col = self.start_row, self.start_col
        self.x, self.y = grid_to_screen(self.start_row, self.start_col)

        self.target_path = []
        self.path_index = 0
        self.speed = config.AMBULANCE_SPEED  # Configurable pixels/second
        self.angle = 0.0    # 0 = RIGHT, 90 = DOWN, 180 = LEFT, 270 = UP

        # Flashing emergency lights timer
        self.siren_timer = 0.0
        self.siren_state = False

    def reset(self):
        """Resets the ambulance back to the starting cell."""
        self.row, self.col = self.start_row, self.start_col
        self.x, self.y = grid_to_screen(self.start_row, self.start_col)
        self.path_index = 0
        self.angle = 0.0
        self.siren_timer = 0.0
        self.siren_state = False

    def set_path(self, path):
        """Sets the initial waypoint path for ambulance navigation."""
        self.target_path = path
        self.path_index = 0
        if path:
            self.row, self.col = path[0]
            self.x, self.y = grid_to_screen(self.row, self.col)

    def update_path(self, new_path):
        """
        Updates waypoint path during dynamic A* rerouting.
        Preserves current physical (x, y) pixel position so no teleportation occurs!
        """
        self.target_path = new_path
        self.path_index = 0
        if new_path:
            self.row, self.col = screen_to_grid(int(self.x), int(self.y))

    def is_at_destination(self):
        """Returns True if ambulance has traversed all waypoints to destination."""
        if not self.target_path:
            return False
        return self.path_index >= len(self.target_path) - 1


    def update(self, dt, is_active):
        """
        Updates ambulance position along the target path using delta time.
        Movement and siren light animation stop when is_active is False.
        """
        if not is_active or not self.target_path:
            return

        # Siren light animation updates ONLY while active / moving
        self.siren_timer += dt
        if self.siren_timer >= 0.15:  # Flash every 150ms
            self.siren_timer = 0.0
            self.siren_state = not self.siren_state


        # Check if destination reached
        if self.path_index >= len(self.target_path):
            return

        target_row, target_col = self.target_path[self.path_index]
        target_x, target_y = grid_to_screen(target_row, target_col)

        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)

        # Update angle facing
        if dist > 1.0:
            target_angle = math.degrees(math.atan2(dy, dx))
            self.angle = target_angle

        # Move towards target waypoint
        step = self.speed * dt
        if dist <= step or dist < 2.0:
            # Reached current waypoint, advance to next
            self.x = target_x
            self.y = target_y
            self.row = target_row
            self.col = target_col
            self.path_index += 1
        else:
            # Interpolate position
            self.x += (dx / dist) * step
            self.y += (dy / dist) * step
            self.row, self.col = screen_to_grid(int(self.x), int(self.y))

    def draw(self, surface):
        """
        Renders a detailed ambulance vector graphic with body, red cross, wheels,
        and flashing emergency siren lights, rotated according to current movement direction.
        """
        # Create vehicle surface with alpha transparency for shadow & smooth rendering
        v_width = 30
        v_height = 20

        veh_surface = pygame.Surface((v_width + 8, v_height + 8), pygame.SRCALPHA)

        # Vehicle Shadow
        shadow_rect = pygame.Rect(4, 6, v_width, v_height)
        pygame.draw.rect(veh_surface, (0, 0, 0, 90), shadow_rect, border_radius=4)

        # Main Chassis (White Body)
        body_rect = pygame.Rect(4, 4, v_width, v_height)
        pygame.draw.rect(veh_surface, (250, 250, 255), body_rect, border_radius=4)
        pygame.draw.rect(veh_surface, (180, 190, 205), body_rect, 1, border_radius=4)

        # Wheels (4 corner positions)
        wheel_w, wheel_h = 6, 3
        # Top-left, Bottom-left, Top-right, Bottom-right
        wheels = [
            (8, 2),
            (8, 4 + v_height - 1),
            (4 + v_width - 10, 2),
            (4 + v_width - 10, 4 + v_height - 1),
        ]
        for wx, wy in wheels:
            pygame.draw.rect(
                veh_surface, (30, 35, 45), (wx, wy, wheel_w, wheel_h), border_radius=1
            )

        # Front Windshield (Right side of vehicle surface when angle = 0)
        windshield = pygame.Rect(4 + v_width - 8, 4 + 3, 5, v_height - 6)
        pygame.draw.rect(veh_surface, (50, 80, 120), windshield, border_radius=1)

        # Side Windows
        pygame.draw.rect(veh_surface, (60, 90, 130), (4 + 10, 4 + 2, 8, 3))
        pygame.draw.rect(
            veh_surface, (60, 90, 130), (4 + 10, 4 + v_height - 5, 8, 3)
        )

        # Roof Red Cross Emblem (Center)
        cx, cy = 4 + v_width // 2 - 2, 4 + v_height // 2
        arm_l, arm_w = 8, 3
        # Vertical arm
        pygame.draw.rect(
            veh_surface,
            config.ACCENT_RED,
            (cx - arm_w // 2, cy - arm_l // 2, arm_w, arm_l),
        )
        # Horizontal arm
        pygame.draw.rect(
            veh_surface,
            config.ACCENT_RED,
            (cx - arm_l // 2, cy - arm_w // 2, arm_l, arm_w),
        )

        # Flashing Emergency Siren Lightbar (Red & Blue on roof)
        siren_y = 4 + v_height // 2 - 4
        siren_x = 4 + v_width - 12

        if self.siren_state:
            c_red = config.ACCENT_RED
            c_blue = (50, 80, 180)
        else:
            c_red = (180, 50, 50)
            c_blue = config.ACCENT_BLUE

        # Red Light
        pygame.draw.circle(veh_surface, c_red, (siren_x, siren_y), 3)
        # Blue Light
        pygame.draw.circle(veh_surface, c_blue, (siren_x, siren_y + 8), 3)

        # Rotate vehicle according to angle
        rotated_surface = pygame.transform.rotate(veh_surface, -self.angle)
        rect = rotated_surface.get_rect(center=(int(self.x), int(self.y)))

        surface.blit(rotated_surface, rect)
