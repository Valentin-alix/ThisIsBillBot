# Bot-DofusUnity

Python 3.12 multi-account automation framework. Main code: `src/`; launcher: `AnkamaLauncherEmulator/`; data extraction and protocol mapping: `DBDofusUnity/`.
GUI uses PyQt6 + FluentWidgets. Both MITM and direct sockets feed protocol decoding -> `EventManager.process_msg()` -> frames update `GameState` -> behaviors react.

## Validation

Run commands from the repository root:

- Targeted tests: `uv run pytest tests/path/to/test_file.py`.
- Lint without edits: `uv run ruff check .`.
- Types: `uv run pyright`.
- Final gate for code changes: `uv run poe verify` (also applies Ruff fixes).

During iteration, run only the relevant check or test. For documentation-only changes, verify paths, commands, and `git diff --check`; application tests are unnecessary.

## Code and tests

- Add concise comments/docstrings only for non-obvious constraints or reasoning; describe current behavior, not change history.
- Validate external input at boundaries. Avoid speculative guards, fallbacks, and defaults; keep required data required and let internal invariant violations fail explicitly.
- For behavior changes, add or update tests only after the implementation has been validated.
- Test meaningful observable behavior, contracts, and regressions; avoid tests of implementation details or tuning values and tests added solely for coverage.
- Type external data explicitly to avoid Pyright `Unknown` errors; prefer existing validation models for fixed schemas. Do not hide errors with `# pyright: ignore`.

## Exploration

- Avoid broad reads/searches of `DBDofusUnity/datas/**`, `DBDofusUnity/Il2CppInspectorRedux/**`, `DBDofusUnity/protodec/**`, `DBDofusUnity/UABEA/**`, and `resources/human_sessions.json` unless needed.
- For protocol definition or mapping changes, read `DBDofusUnity/proto_mapper_assembly/AGENTS.md`, including when editing definitions outside that subtree.
