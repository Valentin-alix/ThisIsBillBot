## Repository Guidelines

## Build, Test, and Development Commands

Use `uv` for local execution:

- `uv sync` installs the locked Python 3.12 environment
- `uv run ruff check . --fix` applies lint fixes
- `uv run pyright` runs static type checks
- `uv run coverage run --source=src -m unittest discover -s tests` executes the test suite

---

## Code Policy

After any code change:

- ALWAYS run:
  - `uv run ruff check . --fix`
  - `uv run pyright`

- DO NOT ignore ruff or pyright rules to make checks pass

- If behavior changed:
  - update existing tests

- If new logic is introduced (function, branch, condition, bug fix):
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

### 3. Surgical Changes

- Modify ONLY what is required
- Do NOT refactor unrelated code
- Match existing style
- Do NOT clean unrelated code

Allowed:
- Remove unused code introduced by YOUR changes

Forbidden:
- Removing pre-existing dead code

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

## Mutability & Data Handling

- No implicit mutation of inputs
- Do not modify arguments unless explicitly documented
- Prefer returning new values

---

## Error Handling

- Fail fast with explicit exceptions
- No silent fallback
- No swallowing errors
- Do NOT return `None` unless part of the contract

---

## Dict Usage

- Use `dict[key]` when key must exist
- Use `.get()` only when absence is expected and handled

---

## Functions & Structure

- Small, composable functions
- Max nesting depth: 3
- Stable helper ordering during refactors
- No legacy shims or compatibility layers
- Prefer direct attribute access
- `getattr` only if absence is expected

---

## Caching

- Only for pure functions:
  - `@functools.cache`
  - `@cached_property`

- No custom caching unless justified

---

## Tooling Constraints

- Do NOT modify application code to satisfy broken third-party typing
- Fix via:
  - stubs
  - configuration

- Verification commands MUST be non-mutating

---

## API Discipline

- Keep the narrowest valid signature
- Do NOT widen interfaces for convenience
- Update all implementations if interface changes
- Handle optional values explicitly at boundaries

---

## Code Quality Rules

- No helpers created only for type checker satisfaction
- Prefer single boundary adapters over scattered casts
- Tests validate runtime behavior ONLY (not lint/type output)