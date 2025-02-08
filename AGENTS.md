## Repository Guidelines

Bot-DofusUnity is a Python 3.12 multi-account automation framework for Dofus 3 Unity. Main source lives in `src/`; workspace members are `AnkamaLauncherEmulatorPremium/` and `DBDofusUnity/`.

## Commands

- `uv run ruff check . --fix` fixes lint issues.
- `uv run pyright` runs type checks.
- `uv run python -m unittest tests/path/to/test_file.TestClass.test_method` runs one test.
- `uv run poe verify` runs lint, type check, and tests.
- `uv run poe dead_code` runs vulture.

Prefer the smallest relevant test/check first. Run full checks only for broad changes or final handoff.

## Large/Generated Paths

Global token/search rules apply. For this repo, also avoid broad reads/searches of `DBDofusUnity/datas/**`, `DBDofusUnity/Il2CppInspectorRedux/**`, `DBDofusUnity/protodec/**`, `DBDofusUnity/UABEA/**`, and `resources/human_sessions.json` unless specifically needed.

## Architecture Map

- GUI: PyQt6 + FluentWidgets.
- Bot orchestration: `BotManager`, `Bot`, `ConnectionHandler`, `BotScheduler`, `ProcessManager`, `BehaviorCoordinator`.
- Network modes: MITM via proxy or direct socket, both feeding the same message pipeline.
- Message pipeline: raw bytes -> protocol decode -> `EventManager.process_msg()` -> modifiers/listeners -> frames update `GameState`; behaviors react.
- Key abstractions: `Behavior`, `EventManager`, immutable `GameState`, `Frame`, PyQt signals.