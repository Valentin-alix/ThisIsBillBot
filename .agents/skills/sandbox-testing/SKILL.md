---
name: sandbox-testing
description: Validate a Behavior/Frame/GameState change against a live running bot via the sandbox CLI - discover, hot-reload, trigger, inspect, without restarting the process
---

# Sandbox-driven behavior testing

Verify a code change against the real bot instead of only reading code or running unit tests.
Everything below goes through `python scripts/sandbox_client.py`, talking to the
`SandboxServer` (`src/services/sandbox/server.py`) running inside the live process
(`SANDBOX_ENABLED` defaults to `True`, `src/consts.py:72`).

Use this whenever a task touches `src/core/behaviors/`, `src/core/frames/`, `src/core/states/`, or
any live game-message handling and a bot can be run to test against.

## 1. Find a bot

```
python scripts/sandbox_client.py --list
```

Returns one line per connected bot: login, account id, `connected`, `in_fight`,
`current_behavior`. Prefer a bot with `in_fight=False` and no `current_behavior` running unless the
test specifically needs a fight/behavior in progress. Add `--json` to get the raw payload.

If nothing is listed, start the bot (`--headless` or GUI) with `SANDBOX_ENABLED=1`.

## 2. Discover before writing code

From here on, pass `--login <login> --code "..."` (or `--file snippet.py`) to run Python against
that bot. Useful entry points already exposed in the sandbox namespace:

- `list_behaviors()` — `{class_name: state}` for every usable behavior, so you don't have to guess
  a class name or state.
- `list_messages(contains="Fight")` — substring search over all known non-obf message names.
- `describe_message("SomeMessage")` — field names for a message, i.e. the kwargs `send_message`
  expects.
- `game_state.debug_snapshot()` — curated, readable summary of map/player/fight/inventory/dialog
  state (`src/core/states/game_state.py:49`). Prefer this over printing `game_state` or
  `event_manager` directly — their default dataclass repr dumps every nested listener/state and is
  unreadable.

## 3. Edit, then hot-reload

Edit the target source file, then apply it to the already-running instances without restarting:

```
python scripts/sandbox_client.py --login <login> --code "reload()"
```

This calls `reload_core_modules()` (`src/services/hotreload/reloader.py`): it reloads changed
modules under `src.core` and repoints already-live instances (behaviors, frames, state objects) at
the new class code in place, preserving their state. Limitations: adding/removing a dataclass field
is not migrated onto existing instances (a process restart is still required for that), and a method
already captured as a bound method before the reload (e.g. inside an already-scheduled timer) keeps
running the old code until the next fresh attribute access.

## 4. Trigger it

- `trigger_behavior("SomeBehavior")` — starts it through `behavior_coordinator.on_play_usable_behavior`.
- `replay_behavior("SomeBehavior")` — replays it in the background.
- `send_message("SomeMessage", field=value, ...)` — injects a message straight into the event
  pipeline as if the server had sent it.

## 5. Confirm

Re-check `game_state.debug_snapshot()`, `behaviors["SomeBehavior"]`, or `list_behaviors()` to
confirm the change had the intended effect before reporting the task done.

## Caution

This acts on a real game account. Avoid irreversible actions (trades, dropping items, spending
kamas, etc.) unless that is explicitly what's being tested.
