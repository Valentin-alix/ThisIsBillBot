# Dofus 3 Automation Framework

This project is a **MITM-based automation framework** for the Dofus 3 client.  
It intercepts network traffic between the client and the server, reconstructs an internal game state, and executes automated behaviors to optimize in-game actions over time.

The project is **state-driven**, **event-based**, and modular, separating:

- Network interception
- State reconstruction
- Decision logic
- Action execution
- GUI monitoring

It is not a simple script bot but a full automation engine.

---

## Core Principles

- Network messages are the single source of truth
- Game state is rebuilt incrementally from intercepted packets
- Logic is deterministic and testable
- GUI never contains game logic

---

## High-Level Architecture

```
Client <-> MITM Proxy <-> Server
                |
                v
           Event Manager
                |
        +-------+--------+
        |                |
     Frames           Behaviors
 (state update)    (action emission)
        |
        v
     Game State
```

### Flow

1. Network packets are intercepted by MITM proxies
2. Packets are decoded and dispatched as events
3. Frames listen to events and update the game state
4. Behaviors read the current state and decide actions
5. Actions are sent back through the proxy

---

## Folder Responsibilities

### `src/controller/`

External coordination and services:

- `scraping_d3_api/` – API scraping clients and request execution
- `bot_config.py` – Config for bot strategies
- `session_timings.py`, `human_timings.py` – Timings and humanization
- `sale_hotel.py` – Sale hotel utilities
- `gfx_mapping.py` – Mapping helpers

---

### `src/core/frames/`

**State reconstruction layer**:

- Each frame listens to specific messages
- Updates dedicated state objects
- Frames do not trigger actions

Examples:

- `map_frame`, `inventory_frame`, `fight_frame`, `player_frame`, `sale_hotel_frame`

---

### `src/core/states/`

**Authoritative in-memory game state**:

- One state per domain (map, inventory, fight, player, etc.)
- Immutable access patterns preferred
- No network or GUI dependencies

---

### `src/core/logic/`

**Game logic and reasoning**:

- Pathfinding
- Damage computation
- Crafting rules
- Item criteria evaluation
- Weighting and optimization algorithms

Submodules:

- `decision/` – Determines actions based on state
- `fight/` – Fight mechanics, effects, spells
- `farms/` – Farming logic, weighted paths
- `items/` – Item utilities, inventory handling
- `movements/` – Map navigation and pathfinding
- `dungeons/`, `craft/`, `economy/` – Specialized logic modules

---

### `src/core/behaviors/`

**Action execution layer**:

- Behaviors read state and emit actions
- One responsibility per behavior
- Examples: `craft_behavior`, `fight_behavior`, `harvester_behavior`, `mule_storage`, `movements/auto_trip`

Behavior priority and orchestration are handled externally.

---

### `src/interfaces/`

Shared contracts:

- Enums
- Interfaces
- Core models
- Observer patterns

Used across all layers.

---

### `src/common/`

Generic utilities:

- Logging
- Timing
- JSON helpers
- Algorithms (A\*)

No dependency on game concepts.

---

### `src/constants/`

Organizes constants into three categories:

- `const.py` – System/OS/network configurations
- `game_constants.py` – Immutable Dofus game data (maps, NPCs, skills)
- `config.py` – Bot parameters, strategies, timings

---

### `src/signals/`

Event signaling layer:

- State change notifications
- UI synchronization

---

### `src/gui/`

**Visualization and control only**:

- PyQt + QFluentWidgets
- Displays state
- Enables or disables behaviors
- GUI must never contain game logic

---

### `src/tools/`

Development and debugging utilities:

- Packet recording
- Profiling
- Scheduling helpers

---

## Behavior Model

- Behaviors are driven by `core.states` and network messages
- Isolated by responsibility
- Never mutate states directly

---

## Configuration

- Lives under `core/config/`
- Includes farming strategies, timings, weights, storage rules
- Read-only at runtime

---

## Critical Areas

- Network message mapping consistency
- State desynchronization handling
- Behavior priority conflicts
- Performance of pathfinding and fight logic

---

## Development Guidelines

- Always type hint
- Avoid broad exception catching
- Keep logic simple and explicit
- Prefer readability over abstraction
- DRY, but clarity first

---

## Tests

- Uses `unittest`
- Tests critical logic only

---

## Commands & Misc

### Mitm

- `poetry run python __main__.py`

![harvest](./docs/pres_harvest.gif)

![automatic_path](./docs/automatic_path.png)

![grid_state](./docs/grid_state.png)

![sniffer](./docs/sniffer.png)

### Profiling

`poetry run python -m cProfile -o benchmark.pstats __main__.py`
`gprof2dot -f pstats benchmark.pstats | dot -Tpng -o benchmark_output.png`

### pyarmor limite à 20 fichiers maxi

`poetry run pyarmor gen -O dist-obf **main**.py src D3Mapping DBDofusUnity D3Database --recursive`

`poetry run pyinstaller --add-data "D3Database/bundles":"D3Database/bundles" --add-data "D3Mapping/d3_mapping/resources":"d3_mapping/resources" --add-data "resources":"resources" --add-data ".venv/Lib/site-packages/wonderwords/assets:wonderwords/assets" **main**.py --noconfirm`
