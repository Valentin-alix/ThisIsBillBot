## How to add a new proto msg

- Add msg in .proto file
- gen python a partir de ce .proto
- Launch add_to_new_dump_cs.py
- Add the pair in pinned_pairs.json
- Launch export_signature_overrides.py
- Launch pipeline mapping

The pin alone places the message: `export_signature_overrides.py` unions mappings **and** pinned
pairs, and an override is what lets a message absent from the non-obf dump.cs enter the workspace.
Its **fields** need a second lap though — the first export has no mapping to read a field mapping
from, so it writes an override with no `field_signatures`, and the message is matched with no field
evidence at all. Pass 1 produces the field mapping, export 2 bakes it in, pass 2 uses it. Do run
that second lap: `messages_access_signature_override.json` is the only file surviving `update-maj`.

A third lap is only for a **nested** message, whose pin the parent's inference can overwrite, or for
a shape you changed in between. `add_to_new_dump_cs.py` wants the composed name (`Owner.Types.Child`
for nested), and a `.proto` shape change invalidates the stored override — delete that entry first,
or the pipeline dies on `Cannot bind field signature at offset N`.

## Filling a group (adding the messages a build added)

`group_similarity_score` is `hungarian_alignment / max(n_non_obf, n_obf)`, so:

- **Never add more messages than the obfuscated side has room for** — it only inflates the
  denominator. `challenge` (15 vs 15) dropped 0.898 -> 0.832 that way, and recovered when pulled.
- **Fill only groups that are coherent**, i.e. where >= 0.90 of the non-obf file descriptor's members
  land in one obf file descriptor. Below that the group is mis-mapped, and filling freezes the error.
  Groups are a stable bijection: 99% of messages keep theirs across builds, 95% within one.
- **Only declare live fields** — no IDA trace and no non-default captured value means the field is
  dropped from `declared_similarity_fields`, so declaring it non-obf creates a phantom. An all-dead
  message is best declared empty, and a nested message only a dead field references is itself dead.
- **Check the obfuscated class is not already mapped** before minting an `Unknown*` name; the
  `.proto` files are not the whole picture, and stealing a class costs more than the group gains.
- **Only messages absent from the non-obf dump.cs can move between `.proto` files** — the dump.cs is
  what defines a message. `stats.proto` -> `fight.proto` worked (no `StatsReflection` exists); the
  same move on `PaddockObjectAnimationPlayEvent` produced a duplicate that landed on junk.
- A package this build ships nothing for holds a wrong class forever: list it in
  `excluded_non_obf.json` rather than deleting its `.proto`, which changes nothing.

Careful: `evidence_coverage is None` means *the message declares no field*, not *no runtime
evidence*. Use the runtime store for the second question.

## Identifying a message

Ranked by how much they actually settle:

1. **Runtime captures.** `capture_sequence` within one `capture_session_id` replays the real client's
   ordering. A Request and its Response sit ~3 ticks apart, which is what separates identical shapes:
   three empty activation requests were told apart purely by the order the user toggled them.
2. **Handler cohort.** The obf trace's `aliases` hold `fft::Boolean m(<msg>)` entries — every message
   a module subscribes to. Strong evidence of the package; it beat the file descriptor on `jsc`.
3. **`stable_callees`** carry unobfuscated names (`DataCenterModule::get_subAreasDataRoot`), naming
   the domain a handler works in.
4. **Orphan reference protos** — a `.proto` mapped nowhere. Best value per effort: `stats.proto`
   supplied 16 named messages at once. Find them by diffing each file's package against the keys.
5. **Type resolution by usage.** To name an obfuscated enum, read the declared type of the matching
   field in mapped messages — that is how `lbl` was identified as `common.Team`.

Do not name fields you cannot order. Knowing a message has three live `int32` does not say which is
which, and a wrong field name is invisible afterwards; `unknown_<key>` stays honest.

## Known mapper behaviours

- A pin is not absolute for a **nested** message: the parent's field mapping registers child matches
  (`discovered_message_matches` -> `register_inferred`) before pinned pairs are selected.
- Messages with two or more `float` fields tend to come back with no field mapping at all — the
  solver cannot separate them and abstains on the whole message.
- `scripts/dump.py:_clear_mapping_inputs_before_pipeline()` wipes `pinned_pairs.json` and the runtime
  captures on `update-maj`. Only `messages_access_signature_override.json` survives, so always run
  `export_signature_overrides.py` after pinning.

## Commands

Full mapper:

```powershell
uv run python main.py run-pipeline
uv run python main.py update-protos
```

Single pair matching debug:

```powershell
uv run python proto_mapper_assembly/scripts/single_pair_match_result.py --obf <ObfClass> --non-obf <NonObfClass>
```

- Computes static and runtime matching details for one candidate message pair.
- Prints score details and field mapping/remapping diagnostics.

Zero-access field inspection:

```powershell
uv run python proto_mapper_assembly/scripts/check_zero_access_fields.py --obf
uv run python proto_mapper_assembly/scripts/check_zero_access_fields.py --non-obf
uv run python proto_mapper_assembly/scripts/check_zero_access_fields.py --obf --explain
```

- Use exactly one of `--obf` or `--non-obf`.
- Add `--explain` to group fields by tracer evidence bucket.
- Prints reports only; it does not write mapper outputs.

Signature override export:

```powershell
uv run python proto_mapper_assembly/scripts/export_signature_overrides.py
uv run python proto_mapper_assembly/scripts/export_signature_overrides.py --obf-dir <path>
```

- Reads detailed mappings, pinned field overrides, dump files, enum signatures, and `new_dump_cs.json`.
- Writes `messages_access_signature_override.json`.
- Use this after generating `game_mappings_detailed.json` or when the obfuscated build changes.

IDA tracing:

```powershell
uv run python proto_mapper_assembly/scripts/ida_tracer_lib/main.py
uv run python proto_mapper_assembly/scripts/ida_tracer_lib/main.py --non-obf
uv run python proto_mapper_assembly/scripts/ida_tracer_lib/main.py --ida-exe <path>
```

- Launches IDA Pro with `ida_proto_field_tracer.py`.
- The IDA script writes `proto_accesses.json`, including enum switch traces.
- Follow `proto_mapper_assembly/scripts/ida_tracer_lib/AGENTS.md` for IDA-specific rules. Do not duplicate or override those lower-level instructions in the root file.

## Script Reference

The user-facing entrypoints under `proto_mapper_assembly/scripts/` are:

- `add_to_new_dump_cs.py`: adds or refreshes selected non-obfuscated protobuf descriptors in `new_dump_cs.json`; use `--dry-run` to inspect changes without writing.
- `audit_client_sent_mappings.py`: scans JSONL bot logs and reports protocol messages missing from `game_mappings.json`, client-origin only by default.
- `audit_historical_assembly_metrics.py`: compares assembly-access and structure metrics across archived builds to measure stability and candidate discrimination.
- `benchmark_cross_build.py`: replays archived builds without pins or signature overrides and scores the matcher against mappings used by the bot in each build's era; writes only its cache.
- `benchmark_no_pins.py`: runs the current matcher without manual pins and compares the result with committed detailed mappings; only `--json` writes a report.
- `check_zero_access_fields.py`: reports protobuf fields absent from the IDA access trace and can explain the likely tracer evidence gap.
- `dump.py`: refreshes dump and generated protobuf artifacts through Il2CppInspectorRedux, protodec, protoc, and IDA; for the live obfuscated build it may archive the previous build, reset mapping inputs, and rerun the pipeline.
- `export_signature_overrides.py`: derives non-obfuscated message access signature overrides from detailed mappings, traces, dumps, and manual bootstrap data.
- `recover_archived_game_mappings.py`: finds the most plausible historical `game_mappings.json` for an archived build from Git history; it writes only with `--write`.
- `single_pair_match_result.py`: explains static score, runtime evidence, field mapping, and remapping diagnostics for one explicit obfuscated/non-obfuscated message pair.
- `ida_tracer_lib/main.py`: launches IDA with `ida_proto_field_tracer.py` and writes `proto_accesses.json`; the other modules in `ida_tracer_lib/` implement that tracer and are not standalone commands.


## Rules

- DO NOT Rely on OFFSET and TAG, they are shuffled on every build.
- Pinned pairs is primarily made to lock a manual mapping so we can generate the messages_access_signature_override.json file to update the signatures of the non-obfuscated messages. The goal is less manual intervention in the mapping for next builds.

## Protocol Mapper Architecture

The full pipeline is implemented by `proto_mapper_assembly.pipeline.run_pipeline()`:

1. `controllers.matching_inputs_loader.load_matching_inputs` loads dumps, signatures, traces, and prepared workspaces.
2. `controllers.pinned_pairs.load_pinned_pairs` loads manually pinned message pairs.
3. `controllers.pinned_pairs.resolve_pinned_pairs_non_obf_targets` resolves pinned non-obfuscated targets.
4. `matching.orchestrator.match_messages` scores and selects message mappings.
5. `export.game_mappings.write_game_mappings` writes `datas/protos/game_mappings.json`.

Main subsystems:

- `interfaces/`: typed data models and contracts shared across the mapper.
- `controllers/`: artifact loading/writing and pipeline input preparation.
- `parsers/`: C# dump, CLR type, protobuf access, and message body parsing.
- `access_signatures.py`: access signature construction from traced functions.
- `scoring/`: similarity between exactly two entities. Knows nothing of the corpus, holds no state.
- `affinities/`: corpus-level signals. Whole corpus in, one `(non_obf, obf)` affinity matrix out. Must not import `matching/`.
- `matching/`: orchestration, score fusion, iterative selection, score lookup, and score constraints.
- `field_mapping/`: field-level matching, scoring, preparation, and ILP-based assignment constraints.
- `runtime/`: runtime trace storage, runtime field validation, and runtime remapping.
- `validators/`: field, global, and message-level validation rules.
- `export/`: final game mapping artifact writers.
- `scripts/`: dump generation, debug tools, IDA trace launcher, and maintenance utilities.

## Protocol Mapper Data Artifacts

Source dumps:

- `OBF_PROTOCOL_GAME_DUMP_CS_FILE`: obfuscated protocol C# dump.
- `NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE`: non-obfuscated protocol C# dump.
- `NON_OBF_NEW_DUMP_CS_FILE`: manual bootstrap input for new non-obfuscated dump data.

Runtime traces:

- `OBF_PROTO_ACCESSES_FILE` and `NON_OBF_PROTO_ACCESSES_FILE`: protobuf field access traces.
- Enum switch/access traces are embedded in `OBF_PROTO_ACCESSES_FILE` and `NON_OBF_PROTO_ACCESSES_FILE`.

Manual inputs:

- `PINNED_PAIRS_FILE`: manually confirmed obfuscated to non-obfuscated message pairs.
- `NON_OBF_SIGNATURE_OVERRIDES_FILE`: manual non-obfuscated signature overrides.
- `new_dump_cs.json`: manual input file used by signature override export.

Generated outputs:

- `GAME_MAPPINGS_JSON_FILE`: final mapper output, written to `datas/protos/game_mappings.json`.
- `OBF_PROTO_OUTPUT` and `NON_OBF_PROTO_OUTPUT`: generated protobuf output directories.

External tools used by scripts:

- `Il2CppInspectorRedux` for IL2CPP layout extraction.
- `protodec` for protobuf definition recovery.
- `protoc` through `PROTOC_PATH` for generated Python bindings.
- IDA Pro for runtime access tracing on game assemblies.
