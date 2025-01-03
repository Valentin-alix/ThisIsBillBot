# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Guidelines

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

---

## Code Policy

After any code change:

- ALWAYS run the smallest relevant verification first:
  - targeted tests for the changed area
  - targeted lint or type checks

- Run full-repo checks when changes are broad or before final handoff:
  - `uv run poe verify`

- DO NOT ignore ruff or pyright rules to make checks pass

- If behavior changed:
  - update existing tests

- If new logic is introduced (function, branch, condition, bug fix):
  - add tests covering:
    - happy path
    - edge cases
    - failure cases when applicable

- Run:
  - smallest relevant tests first
  - then broader repo checks if changes are broad
  - then full suite if changes are broad

---

## Behavioral Guidelines

### 1. Think Before Coding

- State assumptions explicitly
- If multiple interpretations exist, list them
- If unclear → STOP and ask
- Do not guess missing requirements
- Challenge unnecessary complexity

---

### 2. Simplicity First

- Write the minimum code that solves the problem
- No speculative abstractions
- No premature generalization
- No configurability unless required
- No handling of impossible scenarios

Rule:
> If 200 lines can be 50 → rewrite

---

### 4. Goal-Driven Execution

Each task must map to verifiable outcomes:

Examples:

- "Fix bug" → write failing test → fix → test passes
- "Add validation" → write invalid-case tests → implement
- "Refactor" → tests pass before and after

For multi-step tasks:

1. Step → verification
2. Step → verification
3. Step → verification

---

## Coding Style & Naming Conventions

- Python 3.12
- Indentation: 4 spaces
- Line length: 110

### Typing

- All functions MUST have full type annotations
- Use `X | None`, not `Optional[X]`
- Avoid `Any` unless strictly justified
- `object` is FORBIDDEN
- Do NOT use `cast()` unless:
  - boundary case (FFI / external / deserialization)
  - explicitly justified

Replace casts with:
- `isinstance`
- validated constructors
- typed adapters / stubs

- Do NOT silence typing errors
- Fix the type surface instead

---

### Naming

- snake_case → functions, variables, modules
- PascalCase → classes
- UPPER_SNAKE_CASE → constants
- Single-letter names are forbidden

---

## Error Handling

- Fail fast with explicit exceptions
- No silent fallback
- No swallowing errors
- Do NOT return `None` unless part of the contract

---

## Functions & Structure

- No implicit mutation of inputs
- Small, composable functions
- Max nesting depth: 3
- Stable helper ordering during refactors
- No legacy shims or compatibility layers
- Prefer direct attribute access
- Prefer returning new values

---

## Caching

- Only for pure functions:
  - `@python_utils.cache.cache`
  - `@cached_property`

- No custom caching unless justified

---

## API Discipline

- Keep the narrowest valid signature
- Do NOT widen interfaces for convenience
- Update all implementations if interface changes
