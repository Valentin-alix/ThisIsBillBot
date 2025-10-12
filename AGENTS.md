## Repository Guidelines

Bot-DofusUnity is a Python 3.12 multi-account automation framework for Dofus 3 Unity. Main source lives in `src/`; other modules are `AnkamaLauncherEmulatorPremium/` and `DBDofusUnity/`.

## Commands

- `uv run python -m unittest tests/path/to/test_file.TestClass.test_method` runs one test.
- `uv run poe test` runs the full suite with coverage (`coverage run --source=src -m pytest tests`);
  `uv run poe test_verbose` runs it with `pytest -s` instead.
- `uv run poe verify` runs lint, type check, and tests.
- `uv run poe check` runs lint and type check only (no tests).
- `uv run poe lint` runs `ruff check . --fix`; `uv run poe format` runs `ruff format .`.
- `uv run poe dead_code` runs vulture.

During iterative work, run only the relevant verifier — `uv run poe lint`, `uv run poe check_type`, or a single test file — and reserve full `uv run poe verify` for the final gate.

## Pyright strictness

`pyrightconfig.json` enables `reportUnknownVariableType`, `reportUnknownMemberType`, `reportUnknownArgumentType`, `reportUnknownLambdaType`, `reportUnknownParameterType` as **errors**.

Consequence: narrowing from `Any` (e.g. `response.json()`, `json.loads(...)`) via `assert isinstance(value, dict)` produces `dict[Unknown, Unknown]`, which pyright flags on every subsequent indexing. To avoid that:

- Prefer `Model.model_validate(response.json())` over manual narrowing whenever the shape is fixed.
- If you must narrow inline, annotate the source variable explicitly: `body: dict[str, Any] = response.json()` before the assert. The `Any` flows in, the runtime check still fires, and pyright stops complaining about `Unknown`.
- Do **not** silence with `# pyright: ignore` — that hides regressions.

## Large/Generated Paths

For this repo, also avoid broad reads/searches of `DBDofusUnity/datas/**`, `DBDofusUnity/Il2CppInspectorRedux/**`, `DBDofusUnity/protodec/**`, `DBDofusUnity/UABEA/**`, and `resources/human_sessions.json` unless specifically needed.

## Live sandbox

`src/services/sandbox/` lets you run Python against a running `Bot` without restarting it — inject code, send messages, trigger behaviors, fix mapping pairs, inspect `GameState`.

- Enable with `SANDBOX_ENABLED=1` (optional `SANDBOX_PORT`, default 6666), then run the bot (`--headless` or GUI).
- Query it with `python scripts/sandbox_client.py --list` / `--login <login> --code "..."` / `--file snippet.py`, or connect directly with `nc`/telnet.
- Injected scope: `bot`, `game_state`, `event_manager`, `behaviors`, `send_message(name, **fields)`, `trigger_behavior(name)`, `replay_behavior(name)`, `add_pinned_pair(obf_msg_name, non_obf_msg_name, field_mapping_by_obf=None)`.
- GUI equivalent: the "Sandbox" tab next to "Debug" on each account (requires `DEBUG=1`).

### Fixing obf/non-obf message mapping live

`add_pinned_pair` lets you confirm a message (and optionally its field mapping) against a running bot without restarting it:

- Persists the pair to `pinned_pairs.json` (`DBDofusUnity.consts.PINNED_PAIRS_FILE`) via `upsert_pinned_pair` / `upsert_pinned_field_mapping`, so it survives the next `synchronize-protos` pipeline run.
- Immediately patches the in-process `game_mappings` cache via `src/protocol/protocol_game.py::add_pinned_pair_to_game_mappings`, clearing `get_mapping_proto_to_real`/`get_mapping_proto_to_obf` `functools.cache`s — no bot restart, no `game_mappings.json` reload.
- Field mapping keys are `obf_field -> non_obf_field`, same direction as `PinnedPair.field_mapping_by_obf`.
- Workflow: send the sandbox call, then re-trigger the message (replay or wait for it live) and inspect `game_state`/behavior output in the same session to confirm the fix before considering it done.

## Architecture Map

- GUI: PyQt6 + FluentWidgets.
- Bot orchestration: `BotManager`, `Bot`, `ConnectionHandler`, `BotScheduler`, `ProcessManager`, `BehaviorCoordinator`.
- Network modes: MITM via proxy or direct socket, both feeding the same message pipeline.
- Message pipeline: raw bytes -> protocol decode -> `EventManager.process_msg()` -> modifiers/listeners -> frames update `GameState`; behaviors react.
- Key abstractions: `Behavior`, `EventManager`, immutable `GameState`, `Frame`, PyQt signals.