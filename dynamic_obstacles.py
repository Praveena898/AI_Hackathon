"""
dynamic_obstacles.py
---------------------
MEMBER 3 RESPONSIBILITY (blockage half): dynamic traffic blockage
generator.

The blockage is guaranteed to always land ON the ambulance's actual
current path (so the demo never "misses"), but WHERE along that path
it lands, and WHEN (how many steps in) it triggers, is randomized on
every construction of DynamicBlockageController -- i.e. every time
the user clicks START or RESTART. This proves the replanning logic is
genuinely reacting to the obstacle rather than following a hard-coded
script.
"""

import random
import config


class DynamicBlockageController:
    def __init__(self):
        self.triggered = False       # has this run's blockage fired yet?
        self.blockage_cells = set()  # currently active dynamic blockages

        # Randomize per-run: how many steps the ambulance takes before
        # the blockage is placed, and how far ahead on the CURRENT
        # path (at trigger time) the blockage cell is chosen from.
        # Re-rolled every time a new controller is created (i.e. every
        # Start/Restart), so the blockage appears in a different spot
        # each run.
        self.trigger_steps = random.randint(
            config.BLOCKAGE_TRIGGER_STEPS_MIN, config.BLOCKAGE_TRIGGER_STEPS_MAX
        )

    def maybe_spawn_deterministic_blockage(self, ambulance, logger):
        """
        Once the ambulance has taken `self.trigger_steps` steps, pick a
        RANDOM cell from somewhere ahead on its current remaining path
        and turn it into a traffic blockage. Because the cell is
        always sampled from the ambulance's own remaining path, the
        blockage is guaranteed to actually intersect the current
        route -- reliable for a live demo -- while still landing in a
        different place each run.

        Returns the newly blocked cell, or None if nothing spawned
        this frame.
        """
        if self.triggered:
            return None

        if ambulance.steps_taken < self.trigger_steps:
            return None

        remaining = ambulance.remaining_path()

        # Need at least a few cells of path left ahead to place a
        # meaningful, visible blockage (and never block the ambulance's
        # current cell or the hospital itself).
        min_index = 2
        max_index = min(len(remaining) - 2, config.BLOCKAGE_MAX_LOOKAHEAD)

        if max_index < min_index:
            # Ambulance is already close to the hospital -- nothing
            # sensible to block this run.
            self.triggered = True
            return None

        chosen_index = random.randint(min_index, max_index)
        blockage_cell = remaining[chosen_index]

        self.blockage_cells.add(blockage_cell)
        self.triggered = True

        logger.log(f"WARNING: Traffic blockage detected at {blockage_cell}")
        return blockage_cell

    def spawn_random_blockage(self, ambulance, static_obstacles, logger, rng):
        """
        OPTIONAL / future extension: spawn additional blockages at
        random free cells on the remaining path, e.g. repeatedly
        during a single run. Not used by the default single-blockage
        demo, but kept here so the architecture supports it.
        """
        remaining = ambulance.remaining_path()
        candidates = [
            c for c in remaining
            if c not in static_obstacles and c not in self.blockage_cells
            and c not in (ambulance.position, config.GOAL_POS)
        ]
        if not candidates:
            return None
        cell = rng.choice(candidates)
        self.blockage_cells.add(cell)
        logger.log(f"WARNING: Random traffic blockage spawned at {cell}")
        return cell