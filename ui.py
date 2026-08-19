"""
UI components including interactive Buttons, Telemetry Cards, Status Pill Badges,
Event Message Log Feed, and the Emergency Response Information Panel.
"""

# pyrefly: ignore [missing-import]
import pygame
import config


class Button:
    def __init__(self, rect, text, bg_color, hover_color, text_color=config.BTN_TEXT):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont("Helvetica", 14, bold=True)

    def handle_event(self, event):
        """Processes mouse events and returns True if clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, surface):
        """Renders the button with hover and rounded corner styling."""
        color = self.hover_color if self.is_hovered else self.bg_color

        # Button Outer Glow / Shadow on Hover
        if self.is_hovered:
            shadow_rect = self.rect.inflate(4, 4)
            pygame.draw.rect(
                surface, (255, 255, 255, 30), shadow_rect, border_radius=8
            )

        pygame.draw.rect(surface, color, self.rect, border_radius=6)

        # Render Label
        lbl = self.font.render(self.text, True, self.text_color)
        lbl_rect = lbl.get_rect(center=self.rect.center)
        surface.blit(lbl, lbl_rect)


class InfoPanel:
    def __init__(self):
        self.rect = pygame.Rect(
            config.PANEL_X, 0, config.PANEL_WIDTH, config.PANEL_HEIGHT
        )

        # Load Typography
        self.font_title = pygame.font.SysFont("Helvetica", 18, bold=True)
        self.font_subtitle = pygame.font.SysFont("Helvetica", 11, bold=True)
        self.font_header = pygame.font.SysFont("Helvetica", 13, bold=True)
        self.font_body = pygame.font.SysFont("Helvetica", 12, bold=False)
        self.font_bold = pygame.font.SysFont("Helvetica", 12, bold=True)
        self.font_mono = pygame.font.SysFont("Courier", 12, bold=True)
        self.font_event = pygame.font.SysFont("Helvetica", 12, bold=True)

        # Instantiate Buttons with Icons
        btn_w, btn_h = 170, 40
        btn_y = 515
        btn_margin = 15

        # Scenario Mode Selector Button
        self.scenario_mode_btn = Button(
            (config.PANEL_X + 20, 102, config.PANEL_WIDTH - 40, 32),
            "SCENARIO MODE: RANDOM ⚙",
            config.PANEL_CARD_BG,
            config.BTN_PRIMARY_HOVER,
            config.ACCENT_CYAN,
        )


        self.start_btn = Button(
            (config.PANEL_X + 20, btn_y, btn_w, btn_h),
            config.BTN_START_TEXT,
            config.BTN_PRIMARY_BG,
            config.BTN_PRIMARY_HOVER,
        )

        self.pause_btn = Button(
            (config.PANEL_X + 20, btn_y, btn_w, btn_h),
            config.BTN_PAUSE_TEXT,
            config.BTN_PAUSE_BG,
            config.BTN_PAUSE_HOVER,
        )

        self.reset_btn = Button(
            (config.PANEL_X + 20 + btn_w + btn_margin, btn_y, btn_w, btn_h),
            config.BTN_RESET_TEXT,
            config.BTN_RESET_BG,
            config.BTN_RESET_HOVER,
        )


    def draw(
        self,
        surface,
        sim_state,
        amb_row,
        amb_col,
        is_moving,
        progress_pct,
        speed_val,
        event_msg,
        replanning_count=0,
        scenario_title="Random Route Blockage",
        obstacle_pos=None,
        scenario_mode="RANDOM",
    ):
        """Renders the complete telemetry sidebar dashboard."""

        # 1. Background Sidebar Container
        pygame.draw.rect(surface, config.PANEL_BG, self.rect)
        pygame.draw.line(
            surface,
            config.PANEL_BORDER,
            (config.PANEL_X, 0),
            (config.PANEL_X, config.PANEL_HEIGHT),
            2,
        )

        pad_x = config.PANEL_X + 20
        curr_y = 16

        # 2. Header Card
        header_card = pygame.Rect(pad_x, curr_y, config.PANEL_WIDTH - 40, 68)
        pygame.draw.rect(
            surface, config.PANEL_CARD_BG, header_card, border_radius=8
        )
        pygame.draw.rect(
            surface, config.PANEL_BORDER, header_card, 1, border_radius=8
        )

        title = self.font_title.render(config.HEADER_TITLE, True, config.TEXT_COLOR)
        surface.blit(title, (pad_x + 14, curr_y + 12))

        sub = self.font_subtitle.render(
            config.HEADER_SUBTITLE, True, config.ACCENT_CYAN
        )
        surface.blit(sub, (pad_x + 14, curr_y + 38))

        curr_y += 78

        # 3. Scenario Mode Selector Control Button
        self.scenario_mode_btn.text = f"SCENARIO MODE: {scenario_mode} ⚙"
        self.scenario_mode_btn.draw(surface)

        curr_y += 40

        # 4. Status Card
        status_card = pygame.Rect(pad_x, curr_y, config.PANEL_WIDTH - 40, 72)
        pygame.draw.rect(
            surface, config.PANEL_CARD_BG, status_card, border_radius=8
        )
        pygame.draw.rect(
            surface, config.PANEL_BORDER, status_card, 1, border_radius=8
        )

        lbl_status = self.font_subtitle.render("STATUS", True, config.TEXT_MUTED)
        surface.blit(lbl_status, (pad_x + 14, curr_y + 10))

        # Color-coded pill badge
        badge_color = config.ACCENT_YELLOW
        if sim_state == config.STATE_EN_ROUTE:
            badge_color = config.ACCENT_GREEN
        elif sim_state == config.STATE_BLOCKAGE_DETECTED:
            badge_color = config.ACCENT_RED
        elif sim_state == config.STATE_REPLANNING:
            badge_color = config.ACCENT_ORANGE
        elif sim_state == config.STATE_REROUTED:
            badge_color = config.ACCENT_CYAN
        elif sim_state == config.STATE_PAUSED:
            badge_color = config.ACCENT_YELLOW
        elif sim_state == config.STATE_ARRIVED:
            badge_color = config.ACCENT_GREEN
        elif sim_state == config.STATE_READY:
            badge_color = config.ACCENT_BLUE

        badge_rect = pygame.Rect(pad_x + 14, curr_y + 30, 175, 28)
        pygame.draw.rect(surface, badge_color, badge_rect, border_radius=14)

        st_txt = self.font_header.render(sim_state, True, config.BTN_TEXT)
        st_rect = st_txt.get_rect(center=badge_rect.center)
        surface.blit(st_txt, st_rect)

        # Live Indicator Dot
        dot_x = pad_x + 205
        dot_y = curr_y + 44
        dot_c = (
            config.ACCENT_GREEN
            if sim_state in (config.STATE_EN_ROUTE, config.STATE_REROUTED)
            else (config.ACCENT_RED if sim_state == config.STATE_BLOCKAGE_DETECTED else config.TEXT_DIM)
        )
        pygame.draw.circle(surface, dot_c, (dot_x, dot_y), 6)

        curr_y += 84

        # 5. Telemetry Card (Scenario, Position, Blockage Pos, Movement, Speed, Replanning Count, Progress)
        telem_card = pygame.Rect(pad_x, curr_y, config.PANEL_WIDTH - 40, 275)
        pygame.draw.rect(surface, config.PANEL_CARD_BG, telem_card, border_radius=8)
        pygame.draw.rect(surface, config.PANEL_BORDER, telem_card, 1, border_radius=8)

        t_header = self.font_header.render("SYSTEM TELEMETRY", True, config.ACCENT_BLUE)
        surface.blit(t_header, (pad_x + 14, curr_y + 12))
        pygame.draw.line(
            surface,
            config.PANEL_BORDER,
            (pad_x + 14, curr_y + 32),
            (pad_x + config.PANEL_WIDTH - 54, curr_y + 32),
            1,
        )

        ty = curr_y + 38

        # Row 1: Route Variation & Corridor Title
        scen_lbl = self.font_body.render("ROUTE VARIATION:", True, config.TEXT_MUTED)
        surface.blit(scen_lbl, (pad_x + 14, ty))
        scen_val = self.font_bold.render(scenario_title, True, config.ACCENT_CYAN)
        surface.blit(scen_val, (pad_x + 165, ty))

        ty += 24
        # Row 2: Ambulance Position
        pos_lbl = self.font_body.render("AMBULANCE Position:", True, config.TEXT_MUTED)
        surface.blit(pos_lbl, (pad_x + 14, ty))
        pos_val = self.font_mono.render(
            f"({amb_row:02d}, {amb_col:02d})", True, config.TEXT_COLOR
        )
        surface.blit(pos_val, (pad_x + 165, ty))


        ty += 24
        # Row 3: Blockage Position & Route Blocked Status
        blk_lbl = self.font_body.render("BLOCKAGE POSITION:", True, config.TEXT_MUTED)
        surface.blit(blk_lbl, (pad_x + 14, ty))
        blk_str = f"({obstacle_pos[0]:02d}, {obstacle_pos[1]:02d})" if obstacle_pos else "None"
        blk_color = config.ACCENT_RED if obstacle_pos else config.TEXT_DIM
        blk_val = self.font_mono.render(blk_str, True, blk_color)
        surface.blit(blk_val, (pad_x + 165, ty))

        ty += 24
        # Row 4: Route Blocked Status
        rtb_lbl = self.font_body.render("ROUTE BLOCKED:", True, config.TEXT_MUTED)
        surface.blit(rtb_lbl, (pad_x + 14, ty))
        rtb_str = "YES" if obstacle_pos else "NO"
        rtb_color = config.ACCENT_RED if obstacle_pos else config.ACCENT_GREEN
        rtb_val = self.font_bold.render(rtb_str, True, rtb_color)
        surface.blit(rtb_val, (pad_x + 165, ty))


        ty += 24
        # Row 4: Destination
        dest_lbl = self.font_body.render("DESTINATION:", True, config.TEXT_MUTED)
        surface.blit(dest_lbl, (pad_x + 14, ty))
        dest_val = self.font_bold.render("Hospital (13, 18)", True, config.ACCENT_RED)
        surface.blit(dest_val, (pad_x + 165, ty))

        ty += 24
        # Row 5: Movement State
        mov_lbl = self.font_body.render("MOVEMENT:", True, config.TEXT_MUTED)
        surface.blit(mov_lbl, (pad_x + 14, ty))
        mov_str = "Active" if is_moving else ("Paused" if sim_state == config.STATE_PAUSED else "Stopped")
        mov_color = config.ACCENT_GREEN if is_moving else (config.ACCENT_YELLOW if sim_state == config.STATE_PAUSED else config.TEXT_MUTED)
        mov_val = self.font_bold.render(mov_str, True, mov_color)
        surface.blit(mov_val, (pad_x + 165, ty))

        ty += 24
        # Row 6: Speed
        spd_lbl = self.font_body.render("SPEED:", True, config.TEXT_MUTED)
        surface.blit(spd_lbl, (pad_x + 14, ty))
        spd_val = self.font_mono.render(
            f"{int(speed_val)} px/s", True, config.TEXT_COLOR
        )
        surface.blit(spd_val, (pad_x + 165, ty))

        ty += 24
        # Row 7: Replanning Count
        rep_lbl = self.font_body.render("REPLANNING COUNT:", True, config.TEXT_MUTED)
        surface.blit(rep_lbl, (pad_x + 14, ty))
        rep_color = config.ACCENT_ORANGE if replanning_count > 0 else config.TEXT_COLOR
        rep_val = self.font_mono.render(
            f"{replanning_count}", True, rep_color
        )
        surface.blit(rep_val, (pad_x + 165, ty))

        ty += 28
        # Row 8: Progress Bar Track
        prog_lbl = self.font_subtitle.render("ROUTE PROGRESS", True, config.TEXT_MUTED)
        surface.blit(prog_lbl, (pad_x + 14, ty))
        pct_txt = self.font_mono.render(
            f"{int(progress_pct * 100)}%", True, config.TEXT_COLOR
        )
        surface.blit(pct_txt, (pad_x + config.PANEL_WIDTH - 90, ty))

        ty += 16
        p_track = pygame.Rect(pad_x + 14, ty, config.PANEL_WIDTH - 68, 10)
        pygame.draw.rect(surface, config.BG_DARK, p_track, border_radius=5)

        fill_w = max(0, int((config.PANEL_WIDTH - 68) * progress_pct))
        if fill_w > 0:
            p_fill = pygame.Rect(pad_x + 14, ty, fill_w, 10)
            pygame.draw.rect(surface, config.ACCENT_GREEN, p_fill, border_radius=5)

        curr_y += 290

        # 6. Buttons Section
        if sim_state in (config.STATE_EN_ROUTE, config.STATE_REROUTED):
            self.pause_btn.draw(surface)
        else:
            self.start_btn.draw(surface)

        self.reset_btn.draw(surface)

        curr_y += 50

        # 7. Event Message Feed Log Box
        msg_card = pygame.Rect(pad_x, curr_y, config.PANEL_WIDTH - 40, 75)
        pygame.draw.rect(surface, config.PANEL_CARD_BG, msg_card, border_radius=8)
        pygame.draw.rect(surface, config.PANEL_BORDER, msg_card, 1, border_radius=8)

        m_head = self.font_subtitle.render("EVENT LOG / SYSTEM STATUS", True, config.ACCENT_CYAN)
        surface.blit(m_head, (pad_x + 14, curr_y + 10))

        # Dynamic Message Text
        msg_color = config.TEXT_COLOR
        if sim_state == config.STATE_ARRIVED:
            msg_color = config.ACCENT_GREEN
        elif sim_state in (config.STATE_BLOCKAGE_DETECTED, config.STATE_NO_ROUTE):
            msg_color = config.ACCENT_RED
        elif sim_state in (config.STATE_REPLANNING, config.STATE_PAUSED):
            msg_color = config.ACCENT_YELLOW

        msg_surface = self.font_event.render(f"» {event_msg}", True, msg_color)
        surface.blit(msg_surface, (pad_x + 14, curr_y + 36))

        curr_y += 85

        # 8. Hotkeys Footer
        kb_card = pygame.Rect(pad_x, curr_y, config.PANEL_WIDTH - 40, 36)
        pygame.draw.rect(surface, config.BG_DARK, kb_card, border_radius=6)
        pygame.draw.rect(surface, config.PANEL_BORDER, kb_card, 1, border_radius=6)

        kb_txt = self.font_subtitle.render(
            "HOTKEYS:  [SPACE] Start/Pause   |   [R] Reset",
            True,
            config.TEXT_MUTED,
        )
        kb_rect = kb_txt.get_rect(center=kb_card.center)
        surface.blit(kb_txt, kb_rect)


