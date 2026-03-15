# IDA tracer

- Base assembly analysis on verifiable evidence from IDA MCP, IDA scripts, or IDA exports; do not guess behavior.
- Use the official IDA Python API documentation (https://python.docs.hex-rays.com/) as the API reference and reuse existing IDA functionality.
- Keep hand-maintained `typings/` stubs aligned with actual API usage.
- Keep tracing deterministic: identical inputs must produce identical outputs. Justify heuristics and hardcoded offsets with evidence.
