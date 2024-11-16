# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **MITM-based automation framework** for Dofus 3. It intercepts network traffic between the game client and server using man-in-the-middle proxies, reconstructs game state from network packets, and executes automated behaviors. The architecture is **state-driven, event-based, and modular**.

## Development Guidelines

- Always type hint but always use built in python type when it's possible like for example :
  [BAD] : List[int]
  [GOOD] : list[int]
- Don't overcomment things, if the fonction name tell what he does, you don't need to comment anything
- Avoid broad exception catching, for example :
  [BAD] : except Exception
  [GOOD] : except ValueError
- Keep logic simple and explicit
- Prefer readability over abstraction
- DRY, but clarity first
- In tests : always use python built in assert to make pylance happy

## Running the Application

**Main entry point:**

```bash
poetry run python __main__.py
```

This starts the MITM proxy on port 5555 and launches the PyQt GUI.

**Profiling:**

```bash
poetry run python -m cProfile -o benchmark.pstats __main__.py
gprof2dot -f pstats benchmark.pstats | dot -Tpng -o benchmark_output.png
```

**Running tests:**

```bash
poetry run python -m unittest discover tests
```

## Architectural Principles

1. **Network messages are the single source of truth** - All game state derives from intercepted protobuf messages
2. **Frames update state, behaviors emit actions** - Clear separation between state reconstruction and decision-making
3. **EventManager coordinates message flow** - Centralized publish-subscribe system for network events
4. **GUI never contains game logic** - The GUI is strictly for visualization and control

## Core Data Flow

```
Dofus Client <---> MITM Proxy <---> Dofus Server
                       |
                       v
               ProxyListener (src/core/mitm/)
                       |
                       v
               EventManager.process_msg()
                       |
            +----------+-----------+
            |                      |
         Frames                Behaviors
    (listen & update state)  (read state & emit actions)
            |
            v
        GameState
    (authoritative state)
```

## Key Architecture Components

### Bot Class (`src/core/bot/bot.py`)

Central bot instance representing a single Dofus account. Delegates to:

- **ConnectionHandler**: manages connection lifecycle
- **BehaviorCoordinator**: orchestrates behavior priority and execution
- **ProcessManager**: manages the game process lifecycle
- **BotScheduler**: handles playtime scheduling and session management
- **ReplayHandler**: replay recording/playback functionality

### EventManager (`src/core/events_manager/event_manager.py`)

Publish-subscribe system for protobuf messages. Key methods:

- `process_msg(msg)`: dispatches message to registered listeners
- `on(msg_type, callback, originator, priority)`: registers a listener
- `once(msg_type, callback, originator, priority)`: one-time listener
- `before(msg_type, callback, originator)`: message modifier (intercepts before dispatch)

Uses RLock for thread-safety. Listeners are prioritized (frames run before behaviors).

### ProxyListener (`src/core/mitm/proxy_listener.py`)

Creates MITM sockets that intercept Dofus traffic:

- **ConnectionProxy**: handles auth server traffic, identifies bot by PID
- **GameProxy**: handles game server traffic, routes messages to EventManager

### Frames (`src/core/frames/`)

**Responsibility**: Listen to network messages and update game state.

- Register listeners via `event_manager.on(MessageType, callback)`
- Update their corresponding state object (e.g., `MapFrame` updates `MapState`)
- **Never emit actions or contain decision logic**
- Always use `priority=PriorityEnum.FRAME`

Examples: `map_frame.py`, `inventory_frame.py`, `fight_frame.py`, `player_frame.py`

### States (`src/core/states/`)

**Responsibility**: Hold the authoritative in-memory game state.

- Immutable access patterns preferred
- No network or GUI dependencies
- Emit signals via Qt signals for GUI synchronization
- Examples: `MapState`, `InventoryState`, `FightState`, `PlayerState`

All states inherit from `State` base class.

### Behaviors (`src/core/behaviors/`)

**Responsibility**: Read state and emit actions.

- Start/stop lifecycle managed by `BehaviorCoordinator`
- Parent-child hierarchy (stopping parent stops children)
- Register listeners via `event_manager.on()` during `run()`
- Send actions through `game_state.send_msg(message)`
- Clean up listeners with `event_manager.clear_listener_by_origin(self)` in `stop()`

Key behaviors:

- `farms/harvester_behavior.py`: resource harvesting automation
- `farms/fighter_behavior.py`: combat automation
- `craft/craft_behavior.py`: crafting automation
- `movements/auto_trip.py`: automatic pathfinding and travel

All behaviors inherit from `Behavior` base class with lifecycle methods:

- `start(callback, parent, *args, **kwargs)`: initializes behavior
- `run(*args, **kwargs)`: main logic (abstract, must implement)
- `stop()`: cleanup and listener removal

### Logic (`src/core/logic/`)

**Responsibility**: Pure game logic and algorithms.

- `engine/`: domain-specific engines (fights, items, movements, crafts, etc.)
- `decision/`: decision-making algorithms (farm routing, fight tactics, crafting priorities)

Key modules:

- `engine/movements/pathfinding.py`: A\* pathfinding on game maps
- `engine/fights/`: fight simulation, damage calculation, spell mechanics
- `engine/items/`: item utilities, inventory management, criteria evaluation
- `decision/farms/weighted_path.py`: weighted pathfinding for resource optimization

## Subprojects

### D3Mapping

Protobuf mapping between obfuscated and clear protocol definitions. Contains:

- `d3_mapping/`: core mapping logic
- `IL2CppDumper/`: Unity IL2CPP reverse engineering tools
- `protodec/`: protobuf decompilation utilities

### DBDofusUnity

Unity asset bundle extraction tools. Requires:

- protoc-28.0 for protobuf compilation
- UABEA for extracting game data from Unity bundles

Run `poetry run python src/on_init.py` on first launch, then `poetry run python src/on_maj.py` on each game update.

### D3Database

Game data models extracted from Unity bundles. Contains:

- `data_center/`: structured game data (items, maps, monsters, spells)
- `enums/`: game enumerations
- `models/`: Pydantic models for game entities
- `grid/`: map grid representations

## Critical Implementation Patterns

### Adding a New Frame

1. Create class inheriting from `Frame` in `src/core/frames/`
2. Register listeners in `__post_init__` with `self.event_manager.on(MessageType, self.callback, self, self.priority)`
3. Update corresponding state in callback
4. Add frame to `frames` list in `bot_factory.py`

### Adding a New Behavior

1. Create class inheriting from `Behavior` in `src/core/behaviors/`
2. Implement `run(*args, **kwargs)` method
3. Register listeners inside `run()` for state changes
4. Use `self.run_timer()` for delayed execution with human-like timing
5. Call `self.callback()` when complete or `self.stop()` on failure
6. Add behavior to `usable_behaviors` in `bot_factory.py`

### Sending Actions

Always use `game_state.send_msg(message)` to send protobuf messages to the server. Never interact directly with proxies.

### Thread Safety

- `EventManager.lock` is an RLock that must be acquired when mutating state from behaviors
- GUI updates must use Qt signals, never direct mutation
- Use `event_manager.lock` context manager when emitting actions from behaviors

## Important Constants

### `src/const.py`

System and network configuration (proxy ports, connection URLs, file paths).

### `D3Database/consts.py`

Game constants extracted from Unity bundles (map IDs, NPC IDs, item type IDs).

### `src/controller/bot_config.py`

Bot behavior configuration (farming strategies, fight tactics, craft recipes).

## Common Pitfalls

1. **Never mutate state directly from behaviors** - Always use state methods that handle locking and signals
2. **Respect frame/behavior priority** - Frames use `PriorityEnum.FRAME`, behaviors use `PriorityEnum.NORMAL` or lower
3. **Protobuf imports** - Game messages are in `d3_mapping.resources.protos.game.*` and `d3_mapping.resources.protos.connection.*`

## Testing

Tests use `unittest` framework. Located in `tests/`:

- `test_fight/`: fight logic and damage calculation tests
- `test_criterion/`: item criteria evaluation tests
- `fixtures/`: test data generators and mock objects

Run specific test:

```bash
poetry run python -m unittest tests.test_fight.test_spells
```

## Dependencies

Managed with Poetry. Key dependencies:

- PyQt5 + QFluentWidgets: GUI framework
- protobuf: message serialization
- d3-mapping: local package for protobuf mapping
- DBDofusUnity: local package for asset extraction
- D3Database: local package for game data models
