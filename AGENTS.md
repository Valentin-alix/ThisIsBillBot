## Repository Guidelines

Bot-DofusUnity is a Python 3.12 multi-account automation framework for Dofus 3 Unity. Main source lives in `src/`; other modules are `AnkamaLauncherEmulatorPremium/` and `DBDofusUnity/`.

## Commands

- `uv run python -m unittest tests/path/to/test_file.TestClass.test_method` runs one test.
- `uv run poe verify` runs lint, type check, and tests.
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

## Architecture Map

- GUI: PyQt6 + FluentWidgets.
- Bot orchestration: `BotManager`, `Bot`, `ConnectionHandler`, `BotScheduler`, `ProcessManager`, `BehaviorCoordinator`.
- Network modes: MITM via proxy or direct socket, both feeding the same message pipeline.
- Message pipeline: raw bytes -> protocol decode -> `EventManager.process_msg()` -> modifiers/listeners -> frames update `GameState`; behaviors react.
- Key abstractions: `Behavior`, `EventManager`, immutable `GameState`, `Frame`, PyQt signals.