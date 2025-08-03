## Overview

`ida_tracer_lib` traces Protobuf field assignments inside IDA Pro to map obfuscated message fields to non-obfuscated equivalents. Runs as IDA script, walks function call graphs, emits structured field-mapping data for proto mapper pipeline.

`typings/` has hand-maintained IDA API type stubs — keep aligned with actual IDA API usage.

## Commands

```bash
uv run scripts/ida_tracer_lib/main.py --use-obf False  # run on non-obfuscated assembly
uv run scripts/ida_tracer_lib/main.py --use-obf True   # run on obfuscated assembly
```


## IDA MCP Usage

- ALWAYS use ida-pro-mcp tools for:
  - decompilation
  - cross-references
  - instruction inspection

- DO NOT guess assembly behavior without querying IDA

## IDA API Usage

- Use official IDA Python API as source of truth: https://python.docs.hex-rays.com/
- Do NOT reimplement existing IDA functionality
- If behavior is unclear:
  - consult docs or query via MCP

## Determinism

- Tracing logic deterministic
- Same input produces identical output
- No heuristic-based behavior without justification

## Forbidden

- No guessing of IDA behavior
- No hardcoded offsets without justification
