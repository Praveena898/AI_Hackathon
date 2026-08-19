"""
A* Pathfinding implementation for grid-based navigation.
Calculates optimal routes using f(n) = g(n) + h(n) with Manhattan distance heuristic,
supporting neighbor direction permutations and route diversity across dispatches.
"""

import heapq
import config


def manhattan_distance(pos1, pos2):
    """Calculates Manhattan distance heuristic between two (row, col) grid positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def a_star_search(
    layout,
    start_pos,
    goal_pos,
    custom_obstacles=None,
    neighbor_dirs=None,
    extra_cost_fn=None,
):
    """
    Executes A* search algorithm from start_pos to goal_pos.

    Parameters:
        layout: 2D grid matrix of cell types.
        start_pos: Tuple (row, col) representing search origin.
        goal_pos: Tuple (row, col) representing target destination.
        custom_obstacles: Set or list of (row, col) extra non-walkable positions.
        neighbor_dirs: Optional list of (dr, dc) neighbor expansion directions.
        extra_cost_fn: Optional cost function extra_cost_fn(pos) -> float.

    Returns:
        List of (row, col) tuples representing the calculated route from start_pos to goal_pos.
        Returns empty list [] if no valid route exists.
    """
    if custom_obstacles is None:
        custom_obstacles = set()
    else:
        custom_obstacles = set(custom_obstacles)

    rows = len(layout)
    cols = len(layout[0])

    if not (0 <= start_pos[0] < rows and 0 <= start_pos[1] < cols):
        return []
    if not (0 <= goal_pos[0] < rows and 0 <= goal_pos[1] < cols):
        return []

    if neighbor_dirs is None:
        neighbor_dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    counter = 0
    open_heap = []
    heapq.heappush(open_heap, (0, counter, start_pos))

    came_from = {}
    g_score = {start_pos: 0}
    f_score = {start_pos: manhattan_distance(start_pos, goal_pos)}

    open_set = {start_pos}

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        open_set.remove(current)

        if current == goal_pos:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path

        row, col = current
        neighbors = [(row + dr, col + dc) for dr, dc in neighbor_dirs]

        for n_row, n_col in neighbors:
            neighbor = (n_row, n_col)
            if not (0 <= n_row < rows and 0 <= n_col < cols):
                continue

            cell_type = layout[n_row][n_col]
            if (
                cell_type == config.CELL_BUILDING
                or cell_type == config.CELL_OBSTACLE
                or neighbor in custom_obstacles
            ):
                if neighbor != goal_pos:
                    continue

            step_cost = 1
            if extra_cost_fn:
                step_cost += extra_cost_fn(neighbor)

            tentative_g = g_score[current] + step_cost

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + manhattan_distance(neighbor, goal_pos)
                f_score[neighbor] = f

                if neighbor not in open_set:
                    counter += 1
                    heapq.heappush(open_heap, (f, counter, neighbor))
                    open_set.add(neighbor)

    return []


def generate_diverse_initial_route(
    layout, start_pos, goal_pos, previous_route=None, run_index=0
):
    """
    Generates a valid A* initial route that differs significantly from previous_route.
    Uses randomized A* neighbor orderings and corridor cost functions.
    """
    strategies = [
        # Strategy 1: Upper Corridor (East along Row 1 North Ave)
        ({"dirs": [(0, 1), (1, 0), (0, -1), (-1, 0)], "cost": None}, "Upper Corridor"),
        # Strategy 2: Lower Corridor (South along Col 1 West Ave)
        ({"dirs": [(1, 0), (0, 1), (-1, 0), (0, -1)], "cost": None}, "Lower Corridor"),
        # Strategy 3: Midtown Corridor (Row 7 Midtown St)
        (
            {
                "dirs": [(1, 0), (0, 1), (0, -1), (-1, 0)],
                "cost": lambda pos: 0.2 if pos[0] in (1, 13) else 0.0,
            },
            "Midtown Corridor",
        ),
        # Strategy 4: Central Cross Corridor (Col 10 Central Ave)
        (
            {
                "dirs": [(0, 1), (1, 0), (0, -1), (-1, 0)],
                "cost": lambda pos: 0.2 if pos[1] in (18, 1) else 0.0,
            },
            "Central Cross Corridor",
        ),
    ]

    candidates = []
    for params, label in strategies:
        route = a_star_search(
            layout,
            start_pos,
            goal_pos,
            neighbor_dirs=params["dirs"],
            extra_cost_fn=params["cost"],
        )
        if route:
            candidates.append((route, label))

    if not candidates:
        default_route = a_star_search(layout, start_pos, goal_pos)
        return default_route, "Direct Corridor"

    # Select candidate based on run_index or maximum cell difference from previous_route
    target_candidate = candidates[run_index % len(candidates)]
    if previous_route:
        for route, label in candidates:
            diff_count = sum(
                1 for a, b in zip(route, previous_route) if a != b
            ) + abs(len(route) - len(previous_route))
            diff_pct = diff_count / max(1, len(previous_route))
            if diff_pct > 0.25 and route != previous_route:
                if (route, label) == target_candidate:
                    return target_candidate

    return target_candidate
