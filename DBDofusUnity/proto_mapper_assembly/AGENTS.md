# Protocol mapper

## Workflow

Run commands from `DBDofusUnity/`.
After changing `datas/protos/non_obf/game`, add confirmed pairs to `datas/proto_mapper/pinned_pairs.json`, then run `uv run python main.py synchronize-protos` to regenerate bindings and mapping artifacts, export signatures, and run the pipeline.
Run it again after the first pass produces field mappings to persist their signatures. Nested messages or changed shapes may require a third pass; remove incompatible signature overrides first.
`update-maj` clears pins and captures; export overrides again after re-pinning with `uv run python proto_mapper_assembly/scripts/export_signature_overrides.py`.

## Mapping rules

- Name messages and fields only when runtime, protobuf, and static evidence agree; otherwise keep `Unknown*` / `unknown_<key>`.
- Check whether an obfuscated class is already mapped before creating an unknown message.
- Keep only fields observed non-default at runtime or proved by IDA tracing.
- Parent inference can supersede pinned nested pairs. Do not force fields with indistinguishable shapes, especially multiple `float` fields.
- Do not hand-edit generated `excluded_non_obf.json`, `new_dump_cs.json`, Python protobuf bindings, or `game_mappings*.json`; update their sources and regenerate.
