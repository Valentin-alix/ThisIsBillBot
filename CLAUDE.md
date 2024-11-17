# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bot-DofusUnity is a **MITM-based automation framework** for the Dofus 3 client. It intercepts network traffic, reconstructs game state from packets, and executes automated behaviors.

**Core Principle**: Network messages are the single source of truth. Game state is rebuilt incrementally from intercepted packets.

## Commands

```bash
# Run the application
uv run python __main__.py

## Architecture

```

Client <-> MITM Proxy <-> Server
|
v
Event Manager (protobuf messages)
|
+-------+--------+
| |
Frames Behaviors
(state update) (action execution)
|
v
Game State

```

### Key Components

- You can only use protobuf message specified in D3Mapping/d3_mapping/verified_mapping.py, in the values of the dict GAME_VERIFIED_MAPPING_BY_OBF, other message are not mapped to the obfuscated one and therefore can't be used.

**Frames** (`src/core/frames/`): Listen to network packets and update game state. Never trigger actions.
- Register listeners via `event_manager.on()`
- It should never store state, but instead manipulate property in state instances
- Update state objects when events occur

**States** (`src/core/states/`): In-memory game state objects. Behaviors read from state, never modify directly.
- You can store method that return calculated data from states
- Composite root: `GameState` combines all domains
- Thread safety: Protected by `event_manager.lock`

**Behaviors** (`src/core/behaviors/`): Execute actions based on current state.
- Lifecycle: `STOPPED` → `STARTING` → `RUNNING` → `STOPPING` → `STOPPED`
- Must call `finish()` when complete
- Use `unregister_listener()` to clean up specific listeners
- Use `run_timer()` for delayed execution
- Parent-child nesting supported with callback chaining

**Controllers** : In controller folder you must put singleton that manipulate json resources, when you access a controller you must always use directly the class, example :
    [GOOD] : SaleHotelController().get_something()
    [BAD] : controller = SaleHotelController()
            controller.get_something()

**Event Manager** (`src/core/events_manager/`): Central message router with listeners and modifiers.
- Listeners: React to messages (sorted by priority)
- Modifiers: Transform/prevent messages before sending
- Thread-safe with `_RLock`

**Bot** (`src/core/bot/`): Central orchestrator holding references to all components.

### Configuration Structure

- `src/const.py` - System/infrastructure constants (paths, URLs, debug flags)
- `src/core/config.py` - Bot parameters (timings, strategies, limits)
- `src/core/game_constants.py` - Immutable Dofus game data

## Code Style

- Python 3.12+ required
- Use lowercase generics: `list[int]` not `List[int]`
- Prefer composition over inheritance
- DON'T broad exception catching
- Prefer readability over abstraction
- DRY, but clarity first
- Don't comment, the code should be self explanotory
- Fail fast instead of catching unexpected exception

## Behavior Implementation Rules

1. Always call `finish(error_code)` when behavior completes
2. Register event listeners via `event_manager.on()`
3. Clean up listeners in `clear_behavior()` or use `unregister_listener()`
4. Use `run_timer()` for delayed execution (respects behavior lifecycle) or `send_message_delayed()` when sending message with delay
5. Never modify state directly - state updates only through frames
6. Invalid lifecycle transitions throw `BehaviorLifecycleError`

## Thread Safety

- `event_manager.lock` (RLock) protects all state mutations
- Behaviors run inside lock during event processing
- Timers use delayed callback execution inside lock

## External Dependencies

The project uses three git submodules:
- `D3Database` - Game database bundles
- `D3Mapping` - Mapping resource to map obfuscated protobuf message with not obfuscated protobuf message
- `DBDofusUnity` - Additional data

GUI uses PyQt5 with `pyqt-fluent-widgets`.
```
