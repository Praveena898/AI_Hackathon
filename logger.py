"""
logger.py
---------
MEMBER 3 RESPONSIBILITY (logging half): real-time decision log.

Provides a simple reusable `log_event()` call that:
    - timestamps the message relative to simulation start,
    - stores it in a rolling in-memory list for the on-screen panel,
    - and also prints it to the terminal so it is visible even
      without the Pygame window (useful while debugging).
"""

import time


class DecisionLogger:
    def __init__(self, max_visible=14):
        self.start_time = time.time()
        self.entries = []
        self.max_visible = max_visible

    def log(self, message):
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        timestamp = f"[{minutes:02d}:{seconds:02d}]"
        line = f"{timestamp} {message}"
        self.entries.append(line)
        print(line)  # also mirror to terminal
        return line

    def visible_entries(self):
        """Most recent N entries, for display in the side panel."""
        return self.entries[-self.max_visible:]
