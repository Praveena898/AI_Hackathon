import random
from collections import deque
# pyrefly: ignore [missing-import]
import pygame
import config
from grid import Grid
from hospital import Hospital
from ambulance import Ambulance
from ui import InfoPanel
from pathfinding import a_star_search, generate_diverse_initial_route
from scenario import SCENARIO_MODES, select_scenario_obstacle


class Simulation:
    def __init__(self):
        self.grid = Grid()
        self.hospital = Hospital(config.HOSPITAL_POS)
        self.ambulance = Ambulance(config.START_POS)
        self.info_panel = InfoPanel()

        self.run_count = 1
        self.previous_initial_route = None

        # Compute initial route waypoints using diverse A* route generator
        route, corridor_label = generate_diverse_initial_route(
            self.grid.layout,
            config.START_POS,
            config.HOSPITAL_POS,
            previous_route=self.previous_initial_route,
            run_index=self.run_count - 1,
        )
        self.initial_waypoints = route
        self.active_path = self.initial_waypoints[:]
        self.old_blocked_path = None
        self.ambulance.set_path(self.active_path)

        self.state = config.STATE_READY
        self.obstacle_spawned = False
        self.obstacle_pos = None
        self.replanning_count = 0
        self.replan_timer = 0.0

        # Scenario System Attributes
        self.scenario_mode_index = 0  # Default 0: "RANDOM"
        self.current_scenario_title = f"Run {self.run_count} ({corridor_label})"

        # Fonts for canvas header & arrival banner
        self.font_header = pygame.font.SysFont("Helvetica", 22, bold=True)
        self.font_sub = pygame.font.SysFont("Helvetica", 12, bold=False)
        self.font_banner = pygame.font.SysFont("Helvetica", 16, bold=True)

    def cycle_scenario_mode(self):
        """Cycles through SCENARIO_MODES (RANDOM -> Upper -> Lower -> Midtown -> Central Cross)."""
        self.scenario_mode_index = (self.scenario_mode_index + 1) % len(SCENARIO_MODES)

    def start(self):
        """Starts or resumes ambulance movement. Generates a fresh diverse initial route on new dispatch."""
        if self.state == config.STATE_READY:
            # Generate diverse initial route for this run
            route, corridor_label = generate_diverse_initial_route(
                self.grid.layout,
                config.START_POS,
                config.HOSPITAL_POS,
                previous_route=self.previous_initial_route,
                run_index=self.run_count - 1,
            )
            self.active_path = route
            self.ambulance.set_path(self.active_path)
            self.previous_initial_route = route[:]
            self.current_scenario_title = f"Run {self.run_count} ({corridor_label})"
            self.state = config.STATE_EN_ROUTE

        elif self.state == config.STATE_PAUSED:
            if self.replanning_count > 0:
                self.state = config.STATE_REROUTED
            else:
                self.state = config.STATE_EN_ROUTE

    def pause(self):
        """Pauses ambulance movement at its current position."""
        if self.state in (config.STATE_EN_ROUTE, config.STATE_REROUTED):
            self.state = config.STATE_PAUSED

    def toggle_start_pause(self):
        """Toggles between Start/Resume and Pause states."""
        if self.state in (config.STATE_EN_ROUTE, config.STATE_REROUTED):
            self.pause()
        elif self.state in (config.STATE_READY, config.STATE_PAUSED):
            self.start()

    def reset(self):
        """
        Resets ambulance back to original START position, increments run count,
        clears dynamic obstacles, and prepares a fresh diverse route.
        """
        self.run_count += 1
        self.grid.reset_obstacles()
        self.obstacle_spawned = False
        self.obstacle_pos = None
        self.replanning_count = 0
        self.old_blocked_path = None
        self.replan_timer = 0.0

        # Compute next diverse initial A* route
        route, corridor_label = generate_diverse_initial_route(
            self.grid.layout,
            config.START_POS,
            config.HOSPITAL_POS,
            previous_route=self.previous_initial_route,
            run_index=self.run_count - 1,
        )
        self.initial_waypoints = route
        self.active_path = self.initial_waypoints[:]
        self.current_scenario_title = f"Run {self.run_count} ({corridor_label})"

        self.ambulance.reset()  # Resets position back to START (1, 1)
        self.ambulance.set_path(self.active_path)
        self.state = config.STATE_READY


    def handle_event(self, event):
        """Processes user inputs from keyboard and mouse."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.toggle_start_pause()
            elif event.key == pygame.K_r:
                self.reset()

        # Handle Scenario Mode button click
        if self.info_panel.scenario_mode_btn.handle_event(event):
            self.cycle_scenario_mode()
            return

        # Handle UI Button clicks
        if self.info_panel.reset_btn.handle_event(event):
            self.reset()
            return

        if self.state in (config.STATE_EN_ROUTE, config.STATE_REROUTED):
            if self.info_panel.pause_btn.handle_event(event):
                self.pause()
        elif self.state in (config.STATE_READY, config.STATE_PAUSED):
            if self.info_panel.start_btn.handle_event(event):
                self.start()

    def update(self, dt):
        """Updates simulation entities, obstacle detection, and A* rerouting state machine."""
        self.hospital.update(dt)

        is_moving = self.state in (config.STATE_EN_ROUTE, config.STATE_REROUTED)
        self.ambulance.update(dt, is_moving)

        # 1. Dynamic Obstacle Spawning Sequence
        if (
            self.state == config.STATE_EN_ROUTE
            and not self.obstacle_spawned
            and self.ambulance.path_index >= 3  # Allow visible movement after START
        ):
            # Select candidate obstacle cell from future section of active_path
            active_mode = SCENARIO_MODES[self.scenario_mode_index]
            obs_cell, title = select_scenario_obstacle(
                active_mode,
                self.active_path,
                self.ambulance.path_index,
                self.grid.layout,
                config.HOSPITAL_POS,
            )

            self.obstacle_pos = obs_cell
            self.current_scenario_title = title

            # Place dynamic obstacle on grid
            self.grid.set_obstacle(obs_cell[0], obs_cell[1])
            self.obstacle_spawned = True

            # Stop ambulance at CURRENT position and trigger blockage detection
            self.state = config.STATE_BLOCKAGE_DETECTED
            self.replan_timer = 0.8  # Brief pause for visual demonstration

        # 2. Blockage Detection -> Re-planning Delay State
        elif self.state == config.STATE_BLOCKAGE_DETECTED:
            self.replan_timer -= dt
            if self.replan_timer <= 0:
                self.state = config.STATE_REPLANNING
                self.replan_timer = 0.6

        # 3. Re-planning State: Execute A* Search starting from CURRENT Ambulance Position
        elif self.state == config.STATE_REPLANNING:
            self.replan_timer -= dt
            if self.replan_timer <= 0:
                # Save CURRENT ambulance position
                current_amb_pos = (self.ambulance.row, self.ambulance.col)

                # Calculate new A* route starting at CURRENT POSITION avoiding obstacle
                new_route = a_star_search(
                    self.grid.layout,
                    current_amb_pos,
                    config.HOSPITAL_POS,
                    custom_obstacles=[self.obstacle_pos],
                )

                if new_route and len(new_route) > 0:
                    self.old_blocked_path = self.active_path[:]
                    self.active_path = new_route
                    # Update path without changing physical x, y pixel position!
                    self.ambulance.update_path(new_route)
                    self.replanning_count += 1
                    self.state = config.STATE_REROUTED
                else:
                    self.state = config.STATE_NO_ROUTE

        # 4. Destination Arrival Check
        elif is_moving and self.ambulance.is_at_destination():
            self.state = config.STATE_ARRIVED

    def draw(self, surface):
        """Renders simulation grid canvas, obstacle, ambulance, hospital, route path, and telemetry panel."""
        # 1. Fill Canvas Background
        surface.fill(config.BG_DARK)

        # 2. Render Main Header on Simulation Canvas
        hdr_x = config.GRID_OFFSET_X
        hdr_y = 18
        title_txt = self.font_header.render(
            config.HEADER_TITLE, True, config.TEXT_COLOR
        )
        surface.blit(title_txt, (hdr_x, hdr_y))

        sub_txt = self.font_sub.render(
            config.HEADER_SUBTITLE, True, config.ACCENT_CYAN
        )
        surface.blit(sub_txt, (hdr_x, hdr_y + 26))

        # 3. Render Grid with Highlighted Route Path, Old Blocked Path, Hospital, and Ambulance
        self.grid.draw(surface, self.active_path, self.old_blocked_path)
        self.hospital.draw(surface)
        self.ambulance.draw(surface)

        # 4. Render Overlay Banner for Arrival or No Route
        if self.state == config.STATE_ARRIVED:
            banner_w, banner_h = 440, 44
            banner_x = config.GRID_OFFSET_X + (config.GRID_COLS * config.CELL_SIZE - banner_w) // 2
            banner_y = config.GRID_OFFSET_Y + (config.GRID_ROWS * config.CELL_SIZE - banner_h) // 2

            banner_rect = pygame.Rect(banner_x, banner_y, banner_w, banner_h)
            pygame.draw.rect(surface, (46, 213, 115, 60), banner_rect.inflate(8, 8), border_radius=10)
            pygame.draw.rect(surface, config.PANEL_CARD_BG, banner_rect, border_radius=8)
            pygame.draw.rect(surface, config.ACCENT_GREEN, banner_rect, 2, border_radius=8)

            msg_txt = self.font_banner.render("✓ AMBULANCE ARRIVED AT HOSPITAL", True, config.ACCENT_GREEN)
            msg_rect = msg_txt.get_rect(center=banner_rect.center)
            surface.blit(msg_txt, msg_rect)

        elif self.state == config.STATE_NO_ROUTE:
            banner_w, banner_h = 440, 44
            banner_x = config.GRID_OFFSET_X + (config.GRID_COLS * config.CELL_SIZE - banner_w) // 2
            banner_y = config.GRID_OFFSET_Y + (config.GRID_ROWS * config.CELL_SIZE - banner_h) // 2

            banner_rect = pygame.Rect(banner_x, banner_y, banner_w, banner_h)
            pygame.draw.rect(surface, (255, 71, 87, 60), banner_rect.inflate(8, 8), border_radius=10)
            pygame.draw.rect(surface, config.PANEL_CARD_BG, banner_rect, border_radius=8)
            pygame.draw.rect(surface, config.ACCENT_RED, banner_rect, 2, border_radius=8)

            msg_txt = self.font_banner.render("NO VALID ROUTE AVAILABLE", True, config.ACCENT_RED)
            msg_rect = msg_txt.get_rect(center=banner_rect.center)
            surface.blit(msg_txt, msg_rect)

        # 5. Compute Route Progress & Dynamic Event Messages
        total_steps = max(1, len(self.active_path) - 1)
        current_step = min(self.ambulance.path_index, total_steps)
        progress_pct = current_step / total_steps if self.state != config.STATE_READY else 0.0
        if self.state == config.STATE_ARRIVED:
            progress_pct = 1.0

        amb_r, amb_c = self.ambulance.row, self.ambulance.col

        # Determine exact requested Event Log Messages with dynamic coordinates
        obs_str = f"({self.obstacle_pos[0]}, {self.obstacle_pos[1]})" if self.obstacle_pos else ""

        if self.state == config.STATE_READY:
            event_msg = f"New simulation started (Run {self.run_count}). Ready at ({amb_r}, {amb_c})."
        elif self.state == config.STATE_EN_ROUTE:
            event_msg = f"Ambulance en route at ({amb_r}, {amb_c})."
        elif self.state == config.STATE_BLOCKAGE_DETECTED:
            event_msg = f"⚠ Blockage detected at {obs_str}. 🔊 Rerouting..."
        elif self.state == config.STATE_REPLANNING:
            event_msg = f"🔄 Current route invalidated. New route calculating from ({amb_r}, {amb_c})..."
        elif self.state == config.STATE_REROUTED:
            event_msg = f"✓ Alternative route found around {obs_str}. Ambulance continuing."
        elif self.state == config.STATE_PAUSED:
            event_msg = f"Ambulance paused at ({amb_r}, {amb_c})."
        elif self.state == config.STATE_ARRIVED:
            event_msg = "✓ Hospital reached. Mission complete."
        elif self.state == config.STATE_NO_ROUTE:
            event_msg = "❌ NO VALID ROUTE AVAILABLE"
        else:
            event_msg = f"Ambulance continuing from ({amb_r}, {amb_c})."




        # 6. Render Right Telemetry Panel
        is_moving = self.state in (config.STATE_EN_ROUTE, config.STATE_REROUTED)
        self.info_panel.draw(
            surface,
            self.state,
            amb_r,
            amb_c,
            is_moving,
            progress_pct,
            config.AMBULANCE_SPEED,
            event_msg,
            self.replanning_count,
            self.current_scenario_title,
            self.obstacle_pos if self.obstacle_spawned else None,
            SCENARIO_MODES[self.scenario_mode_index],
        )
