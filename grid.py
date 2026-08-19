"""
Grid component responsible for city map representation, cell coordinate conversion,
and rendering of roads, buildings, start depot, and hospital floor pad.
"""

import pygame
import config

# 15 rows x 20 columns layout
# 0 = ROAD, 1 = BUILDING, 2 = START, 3 = HOSPITAL
DEFAULT_MAP_LAYOUT = [
    # 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 0
    [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 1 (Main North Ave, Start at 1,1)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 2
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 3
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 4 (Central East-West St)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 5
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 6
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 7 (Midtown St)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 8
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 9
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 10 (South Ave)
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 11
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1],  # Row 12
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],  # Row 13 (Hospital Ave, Hospital at 13,18)
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 14
]


def grid_to_screen(row, col):
    """
    Converts (row, col) grid indices to pixel center coordinates (x, y).
    """
    x = config.GRID_OFFSET_X + col * config.CELL_SIZE + config.CELL_SIZE // 2
    y = config.GRID_OFFSET_Y + row * config.CELL_SIZE + config.CELL_SIZE // 2
    return x, y


def screen_to_grid(x, y):
    """
    Converts pixel (x, y) coordinates to nearest (row, col) grid indices.
    """
    col = (x - config.GRID_OFFSET_X) // config.CELL_SIZE
    row = (y - config.GRID_OFFSET_Y) // config.CELL_SIZE
    col = max(0, min(config.GRID_COLS - 1, int(col)))
    row = max(0, min(config.GRID_ROWS - 1, int(row)))
    return row, col


class Grid:
    def __init__(self, layout=None):
        self.rows = config.GRID_ROWS
        self.cols = config.GRID_COLS
        self.cell_size = config.CELL_SIZE
        self.layout = [row[:] for row in (layout or DEFAULT_MAP_LAYOUT)]

        # Set special cells explicitly
        start_r, start_c = config.START_POS
        hosp_r, hosp_c = config.HOSPITAL_POS
        self.layout[start_r][start_c] = config.CELL_START
        self.layout[hosp_r][hosp_c] = config.CELL_HOSPITAL

        # Load fonts
        self.font_tiny = pygame.font.SysFont("Helvetica", 10, bold=True)
        self.font_label = pygame.font.SysFont("Helvetica", 12, bold=True)

    def set_obstacle(self, row, col):
        """Places a dynamic traffic blockage obstacle on specified cell."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.layout[row][col] not in (config.CELL_START, config.CELL_HOSPITAL):
                self.layout[row][col] = config.CELL_OBSTACLE

    def clear_obstacle(self, row, col):
        """Clears specified dynamic traffic blockage."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            if self.layout[row][col] == config.CELL_OBSTACLE:
                self.layout[row][col] = config.CELL_ROAD

    def reset_obstacles(self):
        """Clears all dynamic traffic obstacles from grid layout."""
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == config.CELL_OBSTACLE:
                    self.layout[r][c] = config.CELL_ROAD

    def is_walkable(self, row, col):
        """Returns True if cell is walkable road, start, or hospital."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.layout[row][col] not in (config.CELL_BUILDING, config.CELL_OBSTACLE)
        return False

    def draw(self, surface, waypoints=None, old_path=None):
        """Renders grid, buildings, roads, obstacle barriers, and route paths."""
        grid_width = self.cols * self.cell_size
        grid_height = self.rows * self.cell_size

        # Frame & Background
        frame_rect = pygame.Rect(
            config.GRID_OFFSET_X - 4,
            config.GRID_OFFSET_Y - 4,
            grid_width + 8,
            grid_height + 8,
        )
        pygame.draw.rect(surface, config.GRID_BORDER, frame_rect, border_radius=6)

        grid_rect = pygame.Rect(
            config.GRID_OFFSET_X, config.GRID_OFFSET_Y, grid_width, grid_height
        )
        pygame.draw.rect(surface, config.GRID_BG, grid_rect)

        # Render Cells
        for r in range(self.rows):
            for c in range(self.cols):
                cell_x = config.GRID_OFFSET_X + c * self.cell_size
                cell_y = config.GRID_OFFSET_Y + r * self.cell_size
                cell_rect = pygame.Rect(cell_x, cell_y, self.cell_size, self.cell_size)

                cell_type = self.layout[r][c]

                if cell_type == config.CELL_BUILDING:
                    # Building Block
                    pygame.draw.rect(surface, config.BUILDING_COLOR, cell_rect)
                    roof_rect = cell_rect.inflate(-4, -4)
                    pygame.draw.rect(surface, config.BUILDING_ROOF, roof_rect)
                    pygame.draw.rect(surface, config.BUILDING_BORDER, cell_rect, 1)

                    # Window detail
                    w_x, w_y = cell_x + 8, cell_y + 8
                    pygame.draw.rect(surface, config.BUILDING_WINDOW, (w_x, w_y, 6, 6))
                    pygame.draw.rect(surface, config.BUILDING_WINDOW, (w_x + 14, w_y, 6, 6))
                    pygame.draw.rect(surface, config.BUILDING_WINDOW, (w_x, w_y + 14, 6, 6))
                    pygame.draw.rect(surface, config.BUILDING_WINDOW, (w_x + 14, w_y + 14, 6, 6))

                elif cell_type == config.CELL_OBSTACLE:
                    # Render Red Blocked Cell & Traffic Barrier 🚧
                    pygame.draw.rect(surface, config.OBSTACLE_BG, cell_rect, border_radius=4)
                    pygame.draw.rect(surface, config.OBSTACLE_BORDER, cell_rect, 2, border_radius=4)

                    # Draw Yellow Diagonal Hazard Stripes
                    for stripe_offset in range(-10, 40, 10):
                        p1 = (cell_x + stripe_offset, cell_y)
                        p2 = (cell_x + stripe_offset + 10, cell_y + self.cell_size)
                        pygame.draw.line(surface, config.OBSTACLE_STRIPE, p1, p2, 3)

                    # Overlay "🚧 BLOCKED" and (r, c) Coordinate Label Tag
                    b_lbl = self.font_tiny.render("🚧 BLOCKED", True, (255, 255, 255))
                    b_bg = pygame.Rect(cell_x + 1, cell_y + self.cell_size // 2 - 8, self.cell_size - 2, 16)
                    pygame.draw.rect(surface, (180, 0, 0), b_bg, border_radius=3)
                    surface.blit(b_lbl, (cell_x + (self.cell_size - b_lbl.get_width()) // 2, cell_y + self.cell_size // 2 - 7))

                    # Render coordinate tag below cell
                    coord_str = f"({r}, {c})"
                    c_txt = self.font_tiny.render(coord_str, True, config.ACCENT_YELLOW)
                    c_bg = pygame.Rect(cell_x - 4, cell_y + self.cell_size, self.cell_size + 8, 14)
                    pygame.draw.rect(surface, config.PANEL_CARD_BG, c_bg, border_radius=3)
                    pygame.draw.rect(surface, config.ACCENT_RED, c_bg, 1, border_radius=3)
                    surface.blit(c_txt, (cell_x + (self.cell_size - c_txt.get_width()) // 2, cell_y + self.cell_size + 1))


                elif (
                    cell_type == config.CELL_ROAD
                    or cell_type == config.CELL_START
                    or cell_type == config.CELL_HOSPITAL
                ):
                    pygame.draw.rect(surface, config.ROAD_COLOR, cell_rect)
                    pygame.draw.rect(surface, config.GRID_LINE, cell_rect, 1)

                    center_y = cell_y + self.cell_size // 2
                    if (c > 0 and self.layout[r][c - 1] != config.CELL_BUILDING) or (
                        c < self.cols - 1
                        and self.layout[r][c + 1] != config.CELL_BUILDING
                    ):
                        pygame.draw.line(
                            surface,
                            config.ROAD_LINE,
                            (cell_x + 4, center_y),
                            (cell_x + self.cell_size - 4, center_y),
                            1,
                        )

                    if cell_type == config.CELL_START:
                        pygame.draw.rect(
                            surface, config.ACCENT_YELLOW, cell_rect, 2, border_radius=4
                        )
                        s_lbl = self.font_tiny.render("START", True, config.ACCENT_YELLOW)
                        surface.blit(
                            s_lbl,
                            (
                                cell_x + (self.cell_size - s_lbl.get_width()) // 2,
                                cell_y + 2,
                            ),
                        )

        # Draw Old Blocked Path Overlay (if rerouted)
        if old_path and len(old_path) > 1:
            old_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
            old_pts = []
            for r, c in old_path:
                px = c * self.cell_size + self.cell_size // 2
                py = r * self.cell_size + self.cell_size // 2
                old_pts.append((px, py))
                cell_x = c * self.cell_size
                cell_y = r * self.cell_size
                p_rect = pygame.Rect(cell_x + 4, cell_y + 4, self.cell_size - 8, self.cell_size - 8)
                pygame.draw.rect(old_surface, config.OLD_PATH_COLOR, p_rect, border_radius=3)
            if len(old_pts) >= 2:
                pygame.draw.lines(old_surface, (255, 71, 87, 180), False, old_pts, 2)
            surface.blit(old_surface, (config.GRID_OFFSET_X, config.GRID_OFFSET_Y))

        # Highlight Active Route Waypoints (Cyan/Green Path)
        if waypoints and len(waypoints) > 1:
            path_surface = pygame.Surface((grid_width, grid_height), pygame.SRCALPHA)
            pixel_points = []
            for r, c in waypoints:
                px = c * self.cell_size + self.cell_size // 2
                py = r * self.cell_size + self.cell_size // 2
                pixel_points.append((px, py))

                cell_x = c * self.cell_size
                cell_y = r * self.cell_size
                p_rect = pygame.Rect(cell_x + 2, cell_y + 2, self.cell_size - 4, self.cell_size - 4)
                pygame.draw.rect(path_surface, (0, 210, 211, 40), p_rect, border_radius=4)
                pygame.draw.rect(path_surface, (0, 210, 211, 120), p_rect, 1, border_radius=4)

            if len(pixel_points) >= 2:
                pygame.draw.lines(path_surface, (0, 210, 211, 190), False, pixel_points, 3)

            surface.blit(path_surface, (config.GRID_OFFSET_X, config.GRID_OFFSET_Y))

        # Draw Grid Labels Ticks
        for c in range(self.cols):
            cx = config.GRID_OFFSET_X + c * self.cell_size + self.cell_size // 2
            txt = self.font_tiny.render(str(c), True, config.TEXT_MUTED)
            surface.blit(txt, (cx - txt.get_width() // 2, config.GRID_OFFSET_Y - 16))

        for r in range(self.rows):
            ry = config.GRID_OFFSET_Y + r * self.cell_size + self.cell_size // 2
            txt = self.font_tiny.render(str(r), True, config.TEXT_MUTED)
            surface.blit(txt, (config.GRID_OFFSET_X - 18, ry - txt.get_height() // 2))


