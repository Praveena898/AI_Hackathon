"""
Route Diversity & Scenario Engine for Emergency Response Ambulance Simulation.
Guarantees dynamic blockages are selected strictly from future cells of the ambulance's active A* route,
supporting multiple city corridors (Upper, Lower, Midtown, Central Cross).
"""

import random
from pathfinding import a_star_search
import config

# UI Scenario Mode Selector Options
SCENARIO_MODES = [
    "RANDOM",
    "Upper Corridor",
    "Lower Corridor",
    "Midtown Corridor",
    "Central Cross Corridor",
]


def select_scenario_obstacle(scenario_mode, active_path, curr_idx, layout, goal_pos):
    """
    Selects a dynamic blockage coordinate STRICTLY from future cells of active_path.

    Parameters:
        scenario_mode: String in SCENARIO_MODES ("RANDOM", "Upper Corridor", etc.).
        active_path: List of (row, col) waypoints of ambulance's current route.
        curr_idx: Current path_index of ambulance.
        layout: 2D matrix of grid layout.
        goal_pos: Destination (row, col) of hospital.

    Returns:
        Tuple of (obstacle_pos, scenario_title).
    """
    if not active_path or len(active_path) < 3:
        return config.DEFAULT_OBSTACLE_POS, "Route Blockage"

    amb_pos = active_path[min(curr_idx, len(active_path) - 1)]
    path_len = len(active_path)

    # Collect ONLY future cells along active_path (3 to 8 cells ahead)
    ahead_start = min(path_len - 2, curr_idx + 3)
    ahead_end = max(ahead_start + 1, min(path_len - 1, curr_idx + 9))

    future_cells = active_path[ahead_start:ahead_end]

    # Fallback to any future cell if offset range is small
    if not future_cells:
        future_cells = [
            p for p in active_path[curr_idx + 1 : path_len - 1] if p != goal_pos and p != amb_pos
        ]

    # Shuffle future cells to ensure randomness
    candidate_list = list(future_cells)
    random.shuffle(candidate_list)

    for candidate in candidate_list:
        if candidate != goal_pos and candidate != amb_pos:
            if layout[candidate[0]][candidate[1]] != config.CELL_BUILDING:
                alt_route = a_star_search(
                    layout, amb_pos, goal_pos, custom_obstacles=[candidate]
                )
                if alt_route and len(alt_route) > 0:
                    title = f"Route Blockage ({candidate[0]}, {candidate[1]})"
                    return candidate, title

    # Fallback to any valid cell on active_path
    for i in range(curr_idx + 1, path_len - 1):
        candidate = active_path[i]
        if candidate != goal_pos and candidate != amb_pos:
            if layout[candidate[0]][candidate[1]] != config.CELL_BUILDING:
                alt_route = a_star_search(
                    layout, amb_pos, goal_pos, custom_obstacles=[candidate]
                )
                if alt_route and len(alt_route) > 0:
                    return candidate, f"Route Blockage ({candidate[0]}, {candidate[1]})"

    default_pos = active_path[min(curr_idx + 3, path_len - 2)]
    return default_pos, f"Route Blockage ({default_pos[0]}, {default_pos[1]})"
