"""
Configuration constants and settings for Emergency Response Ambulance Simulation.
"""

# Screen Dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 750
FPS = 60

# Grid Dimensions & Layout
GRID_COLS = 20
GRID_ROWS = 15
CELL_SIZE = 36

# Left Panel (Simulation Canvas Area)
CANVAS_WIDTH = 780
CANVAS_HEIGHT = 750

# Center grid inside Canvas Area
GRID_OFFSET_X = (CANVAS_WIDTH - (GRID_COLS * CELL_SIZE)) // 2  # 30 px
GRID_OFFSET_Y = 130  # Leave room for header

# Right Panel (Telemetry & Controls)
PANEL_X = CANVAS_WIDTH
PANEL_WIDTH = SCREEN_WIDTH - CANVAS_WIDTH  # 420 px
PANEL_HEIGHT = SCREEN_HEIGHT

# Cell Types
CELL_ROAD = 0
CELL_BUILDING = 1
CELL_START = 2
CELL_HOSPITAL = 3
CELL_OBSTACLE = 4

# Simulation States
STATE_READY = "READY"
STATE_EN_ROUTE = "EN ROUTE"
STATE_BLOCKAGE_DETECTED = "BLOCKAGE DETECTED"
STATE_REPLANNING = "REPLANNING"
STATE_REROUTED = "REROUTED"
STATE_PAUSED = "PAUSED"
STATE_ARRIVED = "ARRIVED"
STATE_NO_ROUTE = "NO VALID ROUTE"


# Color Palette (Modern Dark Slate Emergency Response Theme)
BG_DARK = (20, 24, 33)
PANEL_BG = (15, 18, 25)
PANEL_CARD_BG = (24, 29, 41)
PANEL_BORDER = (42, 50, 68)

GRID_BG = (28, 33, 46)
GRID_BORDER = (50, 60, 80)
GRID_LINE = (38, 45, 62)

ROAD_COLOR = (42, 48, 62)
ROAD_LINE = (80, 92, 115)
ROAD_DASH = (120, 135, 160)

BUILDING_COLOR = (26, 30, 42)
BUILDING_BORDER = (35, 42, 58)
BUILDING_ROOF = (32, 38, 52)
BUILDING_WINDOW = (65, 80, 110)

# Header Titles
HEADER_TITLE = "EMERGENCY RESPONSE SYSTEM"
HEADER_SUBTITLE = "AMBULANCE DYNAMIC A* NAVIGATION SIMULATION"

# Configurable Speed
AMBULANCE_SPEED = 150  # Pixels per second

# Accent Colors
ACCENT_RED = (255, 71, 87)
ACCENT_BLUE = (30, 144, 255)
ACCENT_GREEN = (46, 213, 115)
ACCENT_YELLOW = (255, 171, 0)
ACCENT_CYAN = (0, 210, 211)
ACCENT_ORANGE = (255, 127, 80)

# Path & Obstacle Highlight Colors
PATH_COLOR = (0, 210, 211, 70)           # Semi-transparent Cyan
PATH_LINE_COLOR = (0, 210, 211, 180)     # Cyan connecting path line
OLD_PATH_COLOR = (220, 50, 50, 120)       # Dim Red for blocked portion of old path
NEW_PATH_COLOR = (46, 213, 115, 200)      # Bright Green for new A* path

OBSTACLE_BG = (235, 47, 6)                # Red Blocked Cell
OBSTACLE_STRIPE = (255, 204, 0)           # Hazard Yellow Stripes
OBSTACLE_BORDER = (255, 255, 255)

TEXT_COLOR = (240, 243, 248)
TEXT_MUTED = (140, 152, 175)
TEXT_DIM = (90, 100, 120)

# Button Labels & Colors
BTN_START_TEXT = "▶ START"
BTN_PAUSE_TEXT = "⏸ PAUSE"
BTN_RESET_TEXT = "↻ RESET"

BTN_PRIMARY_BG = (46, 213, 115)
BTN_PRIMARY_HOVER = (60, 230, 130)
BTN_PAUSE_BG = (255, 171, 0)
BTN_PAUSE_HOVER = (255, 190, 30)
BTN_RESET_BG = (255, 71, 87)
BTN_RESET_HOVER = (255, 95, 109)
BTN_TEXT = (15, 18, 25)

# Positions
START_POS = (1, 1)            # (Row 1, Col 1)
HOSPITAL_POS = (13, 18)       # (Row 13, Col 18)
DEFAULT_OBSTACLE_POS = (1, 10) # Dynamic traffic obstacle cell (Row 1, Col 10)
