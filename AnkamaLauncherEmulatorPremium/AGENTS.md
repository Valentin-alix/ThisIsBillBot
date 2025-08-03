## Architecture Notes

- Emulates Ankama Launcher via Thrift server on port **26116** (game connects here, not real launcher). Dofus RETRO uses text socket server on port **26117**.
- Reads/decrypts existing credentials from `ZAAP_PATH` — user must have logged in via official Ankama Launcher at least once.
- `cytrus-v6` (npm) optional; enables in-app game updates when present. Detected via `shutil.which()`.
- Primary target: Windows.

## Testing scope

A test must exercise **our** code path. Constructing a Pydantic `BaseModel` and asserting `model_dump()` equals a dict, or asserting that a missing field raises `ValidationError`, tests Pydantic — drop those tests; Pydantic has its own suite.

Heuristic: if removing the BaseModel changes the test result, it's a Pydantic test. If removing **our** function under test changes the result, it's a real test.

This applies symmetrically to other libraries (requests, playwright, etc.).