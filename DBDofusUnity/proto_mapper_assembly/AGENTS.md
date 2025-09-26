# Protocol mapper

## Workflow

After changing `datas/protos/non_obf/game`, run:

```powershell
uv run python main.py synchronize-protos
```

It regenerates Python bindings, removes orphaned bindings, rebuilds every `new_dump_cs.json` entry,
preserves known offsets, regenerates exclusions, removes obsolete mapping targets, exports overrides,
and runs the pipeline. Add confirmed pins manually to `pinned_pairs.json` before synchronization.

Run it a second time after the first pipeline produces field mappings: the second export stores these
signatures. A nested message or changed shape can need a third pass; remove an incompatible override
first.

## Mapping rules

- Name a message or field only when runtime, protobuf, and static evidence agree. Otherwise keep
  `Unknown*` / `unknown_<key>`.
- Check that an obfuscated class is not already mapped before creating an unknown message.
- Keep only fields observed non-default at runtime or proved by IDA tracing.
- A pinned nested pair can be superseded by parent inference.
- Do not force fields with indistinguishable shapes, especially multiple `float` fields.
- Do not edit `excluded_non_obf.json`: it is generated from C# classes absent from `non_obf/game`.

## Useful commands

```powershell
uv run python main.py run-pipeline
uv run python proto_mapper_assembly/scripts/export_signature_overrides.py
uv run python proto_mapper_assembly/scripts/single_pair_match_result.py --obf <ObfClass> --non-obf <NonObfClass>
uv run python proto_mapper_assembly/scripts/check_zero_access_fields.py --obf --explain
uv run python proto_mapper_assembly/scripts/check_zero_access_fields.py --unknown-fields
uv run python proto_mapper_assembly/scripts/benchmark_cross_build.py --mode current
uv run python proto_mapper_assembly/scripts/group_match_candidates.py --incoherent
uv run python proto_mapper_assembly/scripts/group_match_candidates.py --non-obf Breach --members
```

`group_match_candidates` works at the file-descriptor level: it ranks the obfuscated groups a
`.proto` could belong to and says how much the claim in place is worth, counting the pins behind
it. A group held on 18 messages and no pin is an algorithm's guess and worth contesting; one held
on 6 messages and 4 pins is not. Since the file partition survives a rebuild, anchoring two or
three pins in the right group is enough for the file-descriptor affinity to carry the rest.

`check_zero_access_fields --unknown-fields` classifies every declared `unknown_*` field as
`active` / `dead_candidate` / `inconclusive` by crossing the IDA trace with the runtime captures.
`benchmark_cross_build` grades the matcher: `--mode current` on the working set with no pin,
`--mode cross-build` by replaying each archived build against the mappings of its own era.

`update-maj` clears pins and captures: export overrides again after re-pinning.

## Artifacts

- `pinned_pairs.json`: manually confirmed pairs.
- `messages_access_signature_override.json`: persistent signatures from mappings and pins.
- `new_dump_cs.json`: generated mirror of `non_obf/game`, used by overrides; do not edit it.
- `game_mappings.json` and `game_mappings_detailed.json`: pipeline outputs.
- `proto_accesses.json`: IDA trace; runtime captures provide complementary evidence.
