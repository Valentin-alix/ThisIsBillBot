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

- DO NOT ignore ruff rule or pyright rule to make check passed.

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
- DO NOT silence typing errors with casts or Protocol hacks; fix the type surface or add stubs
- Treat optionality as part of the contract; never cast away `None`
- `object` is FORBIDDEN as a type placeholder; it provides no usable type information
- DO NOT use `cast()` to force a type; fix the source type or introduce proper narrowing
- `cast()` is only allowed at a strict boundary (FFI, external lib, deserialization) and must be justified
- Replace unsafe casts with:
  - explicit type narrowing (`isinstance`)
  - validated constructors
  - typed adapters or stubs

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
- Do NOT add generic wrappers (*args/**kwargs) unless forwarding to a real API
- Prefer direct attribute access; use `getattr` only when absence is expected

### Caching

- Use `@functools.cache` or `@cached_property` ONLY for pure functions (no side effects, deterministic inputs)
- Do NOT implement custom caching unless strictly necessary and justified

## Tooling Constraints

- Do NOT change application code to satisfy broken third-party typing
- Fix via stubs or configuration first
- Verification commands MUST be non-mutating (no hidden behavior changes)

## API Discipline

- Keep the narrowest valid signature; do NOT widen for convenience
- Do NOT change shared interfaces without updating all implementations
- Optional values must be handled explicitly at boundaries

## Code Quality Rules

- Do NOT introduce helpers only to satisfy the type checker
- Prefer a single boundary adapter over scattered casts
- Tests MUST validate runtime behavior, not typing or lint output