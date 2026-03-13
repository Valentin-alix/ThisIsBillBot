Bot-DofusUnity is a Python 3.12 multi-account automation framework for Dofus 3 Unity. Main source lives in `src/`; other modules are `AnkamaLauncherEmulator/` and `DBDofusUnity/`.

## Architecture Map

- GUI: PyQt6 + FluentWidgets.
- Bot orchestration: `BotManager`, `Bot`, `ConnectionHandler`, `BotScheduler`, `ProcessManager`, `BehaviorCoordinator`.
- Network modes: MITM via proxy or direct socket, both feeding the same message pipeline.
- Message pipeline: raw bytes -> protocol decode -> `EventManager.process_msg()` -> modifiers/listeners -> frames update `GameState`; behaviors react.
- Key abstractions: `Behavior`, `EventManager`, immutable `GameState`, `Frame`, PyQt signals.

## Commands

- `uv run python -m unittest tests/path/to/test_file.TestClass.test_method` runs one test.
- `uv run poe test` runs the full suite with coverage (`coverage run --source=src -m pytest tests`);
  `uv run poe test_verbose` runs it with `pytest -s` instead.
- `uv run poe verify` runs lint, type check, and tests.
- `uv run poe check` runs lint and type check only (no tests).
- `uv run poe lint` runs `ruff check . --fix`; `uv run poe format` runs `ruff format .`.
- `uv run poe dead_code` runs vulture.

During iterative work, run only the relevant verifier — `uv run poe lint`, `uv run poe check_type`, or a single test file — and reserve full `uv run poe verify` for the final gate.

## Comments and Docstrings

- Only add comments or docstrings when necessary to explain non-obvious behavior, constraints, or reasoning.
- Keep them concise and describe only the current state of the code; never use them as changelogs or historical notes.
- Do not restate obvious code. Prefer self-explanatory code whenever possible.

## Defensive Code

- Only add defensive code when there is a concrete, demonstrated need.
- Do not add speculative guards, fallbacks, `try`/`except`, default values, or `None` handling for states that should not occur by contract or business rules.
- Required business data must remain required; do not make it optional or provide defaults for convenience.
- Do not hide invalid internal states. Let invariant violations fail explicitly.
- Validate and handle uncertainty at real boundaries (external input, APIs, I/O), not throughout trusted internal code.

## Tests

- For new features or behavior changes, only add or update tests after the implementation has been validated; do not write tests upfront for behavior that may still change.
- Only add tests that provide meaningful long-term value by protecting important behavior, invariants, edge cases, or regressions.
- Test observable behavior and contracts, not implementation details, constants, configuration values, or arbitrary tuning parameters.
- Tests should survive non-behavioral changes such as `threshold=0.4` becoming `threshold=0.5`.
- Prefer fewer high-value tests over brittle or exhaustive low-value coverage. Do not add tests solely to increase coverage.

## Pyright strictness

`pyrightconfig.json` enables `reportUnknownVariableType`, `reportUnknownMemberType`, `reportUnknownArgumentType`, `reportUnknownLambdaType`, `reportUnknownParameterType` as **errors**.

Consequence: narrowing from `Any` (e.g. `response.json()`, `json.loads(...)`) via `assert isinstance(value, dict)` produces `dict[Unknown, Unknown]`, which pyright flags on every subsequent indexing. To avoid that:

- Prefer `Model.model_validate(response.json())` over manual narrowing whenever the shape is fixed.
- If you must narrow inline, annotate the source variable explicitly: `body: dict[str, Any] = response.json()` before the assert. The `Any` flows in, the runtime check still fires, and pyright stops complaining about `Unknown`.
- Do **not** silence with `# pyright: ignore` — that hides regressions.

## Large/Generated Paths

For this repo, also avoid broad reads/searches of `DBDofusUnity/datas/**`, `DBDofusUnity/Il2CppInspectorRedux/**`, `DBDofusUnity/protodec/**`, `DBDofusUnity/UABEA/**`, and `resources/human_sessions.json` unless specifically needed.
