# Protocol mapper

## Workflow

Run commands from `DBDofusUnity/`.
After changing `datas/protos/non_obf/game`, add confirmed pairs to `datas/proto_mapper/pinned_pairs.json` and run `uv run python main.py synchronize-protos`.
Repeat to persist field signatures; nested messages or changed shapes may need a third pass. Remove incompatible signature overrides first.
`update-maj` clears pins and captures; export overrides again after re-pinning with `uv run python proto_mapper_assembly/scripts/export_signature_overrides.py`.

## Mapping rules

- Name messages and fields only when runtime, protobuf, and static evidence agree; otherwise keep `Unknown*` / `unknown_<key>`.
- Check whether an obfuscated class is already mapped before creating an unknown message.
- Keep only fields observed non-default at runtime or proved by IDA tracing.
- Parent inference can supersede pinned nested pairs. Do not force fields with indistinguishable shapes, especially multiple `float` fields.
- Do not hand-edit generated `excluded_non_obf.json`, `new_dump_cs.json`, Python protobuf bindings, or `game_mappings*.json`; update their sources and regenerate.

## Validators and IDA

- Validators return `False` for invalid input; let unexpected exceptions propagate. Fields in `global_validators` and `set_validators` cannot be nested: nested messages are not remapped.
- Key `VALIDATORS_ON_FIELD` by generated protobuf classes (`type[Message]`), with string field names checked against descriptors at import. Group entries by source module.
- Base IDA analysis, heuristics, and offsets on verifiable MCP, script, or export evidence. Identical tracing inputs must produce identical outputs.
- Reuse IDA APIs from https://python.docs.hex-rays.com/ and keep local `typings/` stubs aligned with usage.
