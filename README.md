# Emergency Response Ambulance Simulation (Coordinate-Based A* Rerouting)

A modern, clean, and modular Python Pygame application built for an academic project demonstration. The simulation models an emergency response ambulance dispatching from a start depot, detecting a dynamic road blockage at specific grid coordinates `(row, column)`, and automatically executing **A* Pathfinding** from its current position to calculate an alternative route to the hospital.

---

## 🚑 Key Features & Demonstration Scenarios

### Coordinate-Based Scenario Modes:
- **`RANDOM`** *(Default)*: Randomly selects a valid road blockage coordinate on the ambulance's route on every `START`.
- **`(6, 7)`**: Dynamic blockage placed at Row 6, Col 7.
- **`(8, 10)`**: Dynamic blockage placed at Row 8, Col 10.
- **`(10, 14)`**: Dynamic blockage placed at Row 10, Col 14.
- **`(4, 9)`**: Dynamic blockage placed at Row 4, Col 9.

### Demonstration Sequence:
1. **Ambulance Dispatches**: Ambulance departs from `START` `(Row 1, Col 1)` toward `Hospital (13, 18)`.
2. **Dynamic Blockage Appears**: A `🚧 BLOCKED` hazard barrier appears at the selected coordinate (e.g. `(6, 7)`).
3. **Blockage Detection & Halt**: Ambulance detects the blockage ahead and stops at its **CURRENT position** `(5, 7)`.
4. **Live A* Search from Current Position**: A* calculates a new optimal route starting from `(5, 7)`, avoiding `(6, 7)`. Zero teleportation to start occurs.
5. **Alternative Route & Hospital Arrival**: Ambulance continues along the new route and arrives safely at the hospital.

---

## ⌨️ Controls & Keybindings

| Control | Mouse Button | Keyboard Shortcut | Action |
| :--- | :--- | :--- | :--- |
| **Scenario Mode Selector** | Click `SCENARIO MODE` Button | — | Cycles through `RANDOM`, `(6, 7)`, `(8, 10)`, `(10, 14)`, `(4, 9)` |
| **Start Dispatch** | Click `▶ START` Button | `SPACE` | Begins or resumes ambulance movement toward hospital |
| **Pause Dispatch** | Click `⏸ PAUSE` Button | `SPACE` | Pauses active ambulance movement |
| **Reset Simulation**| Click `↻ RESET` Button | `R` | Removes dynamic obstacle, resets replanning count, and restores ambulance to `(1, 1)` |

---

## 📋 Requirements

- Python 3.8 or higher
- `pygame` (specified in `requirements.txt`)

---

## 🚀 Installation & Setup

1. **Clone or Navigate to Project Directory**:
   ```bash
   cd /path/to/AIHACKATHON
   ```

2. **Activate Virtual Environment**:
   ```bash
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🎮 How to Run

Execute the main application script:

```bash
python main.py
```

---

## 📁 Project Structure

```
.
├── main.py              # Application entry point & Pygame 60 FPS loop
├── config.py            # Global constants (dimensions, colors, positions, states)
├── pathfinding.py       # Grid-based A* algorithm (f(n) = g(n) + h(n))
├── scenario.py          # Coordinate scenario selection & road validation engine
├── grid.py              # City grid matrix, 🚧 hazard barrier & coordinate tag rendering
├── ambulance.py         # Ambulance vector graphic, rotation, sirens, smooth interpolation
├── hospital.py          # Hospital building graphics, red cross emblem, target glow
├── ui.py                # Telemetry dashboard, scenario mode button, event log feed
├── simulation.py        # Master simulation state controller and live A* rerouting coordinator
├── requirements.txt     # Dependency list (pygame)
└── README.md            # Project documentation and user guide
```
