# Repository Guidelines

## Build, Test, and Development Commands
Use `uv` for local execution:

- `uv sync` installs the locked Python 3.12 environment.
- `uv run ruff check . --fix` applies lint fixes.
- `uv run pyright` runs static type checks.
- `uv run coverage run --source=src -m unittest discover -s tests` executes the test suite.

## Code policy

After any code change:

- ALWAYS run:
  - `uv run ruff check . --fix`
  - `uv run pyright`

- If behavior changed:
  - update existing tests

- If new logic is introduced (function, branch, condition, or bug fix):
  - add tests covering:
    - happy path
    - edge cases
    - failure cases when applicable

- A task is NOT complete if:
  - code was modified AND
  - no test was added or updated

- Run:
  - smallest relevant tests first
  - then full suite if changes are broad

## Coding Style & Naming Conventions

- Target: Python 3.12
- Indentation: 4 spaces, no tabs
- Line length: 110 (enforced by ruff)

### Typing

- All functions MUST have full type annotations (args + return)
- Use `X | None` instead of `Optional[X]`
- Avoid `Any` unless strictly unavoidable (must be justified)
- Prefer explicit typed structures over untyped dicts

### Naming

- Modules / functions / variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Single-letter variable names are forbidden

### Mutability & Data Handling

- No implicit mutation of inputs
- Functions must not modify arguments unless explicitly documented
- Prefer returning new values over in-place modification

### Error Handling

- Fail fast: raise explicit exceptions
- Do NOT silently fallback or swallow errors
- Do NOT return `None` for error cases unless part of the type contract

### Dict usage

- Use `dict[key]` when the key is expected to exist
- Use `.get()` ONLY when absence is expected and explicitly handled

### Functions & Structure

- Prefer small, composable functions
- Avoid deep nesting (>3 levels)
- Keep helper ordering stable during refactors
- Do NOT reintroduce dead compatibility layers or legacy shims

### Caching

- Use `@functools.cache` or `@cached_property` ONLY for pure functions (no side effects, deterministic inputs)
- Do NOT implement custom caching unless strictly necessary and justified