## Repository Guidelines

## Setup

```bash
cp .env.example .env  # then configure paths (PC_ID, OPENAI_API_KEY, BOT_SHARED_DATAS_DIR, etc.)
uv sync               # install locked Python 3.12 environment
```

## Build, Test, and Development Commands

Use `uv` for local execution:

- `uv sync` installs the locked Python 3.12 environment
- `uv run ruff check . --fix` runs lint checks
- `uv run pyright` runs static type checks
- `uv run python -m unittest tests/path/to/test_file.TestClass.test_method` runs a single test
- `uv run poe verify` runs everything: lint + type check + tests
- `uv run poe dead_code` runs vulture dead-code detection

---

## Architecture

Bot-DofusUnity is a multi-account automation framework for Dofus 3 (Unity). It supports both MITM proxy and direct socket connections and exposes a PyQt6 GUI.

### Layer Overview

```
GUI (PyQt6 + FluentWidgets)
  └─ BotManager            # one Bot per account
       └─ Bot              # holds state + delegates
            ├─ ConnectionHandler   # lifecycle, reconnect
            ├─ BotScheduler        # playtime windows
            ├─ ProcessManager      # Dofus process
            └─ BehaviorCoordinator # orchestrates behaviors

Network layer (two modes, same message pipeline downstream):
  ├─ MITM  →  ProxyListener  →  ConnectionProxy / GameProxy
  └─ Socket →  SocketClient   →  GameClient

Message pipeline:
  raw bytes → Protocol (varint + Protobuf decode)
            → EventManager.process_msg()
                ├─ Modifiers   (transform obfuscated ↔ plain)
                └─ Listeners   (priority-ordered)
                     ├─ Frames      → update GameState
                     └─ Behaviors   → react to state
```

### Key Abstractions

**`Behavior`** (`src/core/behaviors/`) — all bot actions inherit this base class.  
Lifecycle: `STOPPED → STARTING → RUNNING → STOPPING`. Behaviors compose into trees (e.g. `HarvesterBehavior → RandomFarmBehavior → MapMoveBehavior`). Each registers/cleans up its own EventManager listeners.

**`EventManager`** (`src/core/events_manager/`) — central message bus. Listeners subscribe by Protobuf message type with a priority level. Thread-safe (RLock). Modifiers run before listeners.

**`GameState`** (`src/core/states/`) — immutable dataclass snapshot: `EntityState`, `FightState`, `InteractiveState`, `InventoryState`, `MapState`, `PlayerState`, etc. Frames update it; behaviors read it.

**`Frame`** (`src/core/frames/`) — thin message handler. Subscribes to specific message types via EventManager and writes to `GameState`.

**Signals** (`src/core/signals/`) — PyQt signals for cross-thread communication. `SharedSignals` is global; `BotSignals` is per-bot. GUI, behaviors, and bot lifecycle communicate through these.

### Workspace Layout

Three interdependent `uv` workspace members:

| Directory | Role |
|---|---|
| `src/` | Main bot source (behaviors, engine, GUI, protocol, frames, states) |
| `AnkamaLauncherEmulatorPremium/` | Account auth, launcher emulation, MITM proxy infra |
| `DBDofusUnity/` | Game data extraction, protocol mapping, generated Protobuf stubs |

### Connection Flow

1. GUI "Play" → `BotSignals.play` → `BotManager.on_launch_account()`
2. Socket mode: `SocketClient.connect()` creates `GameClient`; MITM mode: launcher starts Dofus through `ProxyListener`
3. `ConnectionBehavior → GameSessionBehavior` → handshake → `ConnectionHandler.on_ready_to_play()`
4. `BehaviorCoordinator` starts configured behaviors
