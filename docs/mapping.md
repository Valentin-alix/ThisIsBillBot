# Protobuf protocol mapping

[Back to the README](../README.md)

## Why mapping must be rebuilt for every release

Dofus exchanges protobuf messages between the client and servers. The bot needs
readable names and types for these messages so it can decode them and send them
to frames.

Every new game build obfuscates protobuf class and field names again. A mapping
that is valid for one build, such as `hea` to `GameMessage`, may therefore be
wrong in the next one. After every update, regenerate the obfuscated data, rerun
the mapper, and review its results. A pipeline that completes without errors does
not by itself guarantee that every mapping is correct.

## How the mapper works

The mapper compares the installed build's obfuscated protocol with the
unobfuscated protobuf definitions stored in the repository. It combines several
signals:

- message and field structure;
- access signatures extracted from code with IDA Pro;
- message groups, ordering, and parent-child relationships;
- messages actually observed by the sniffer during a session;
- manually confirmed message and field pairs.

The pipeline searches for a consistent assignment between the two protocols and
writes, among other files:

- `datas/protos/game_mappings.json`, used by the bot;
- `datas/protos/game_mappings_detailed.json`, containing scores, confidence indicators, and unmatched fields;
- `datas/proto_mapper/pinned_pairs.json`, preserving manually confirmed mappings between pipeline runs.

The `game_mappings*.json` files, Python protobuf bindings,
`datas/proto_mapper/excluded_non_obf.json`, and
`datas/proto_mapper/non_obf/new_dump_cs.json` are generated. Do not edit them
directly: update their sources, add confirmed pairs, and regenerate them.

## Processing a new build

Run commands from `DBDofusUnity/`:

```powershell
uv run python main.py update-maj
```

This command updates game data, extracts the new protocol, runs the IDA analysis
specified by the configuration, and starts an initial mapper pass. When it
detects an assembly change, it archives the previous runtime capture and resets
`pinned_pairs.json`: old obfuscated names must not be reused without verification.

To regenerate IDA traces separately, use:

```powershell
uv run python main.py ida
```

Then run the bot and sniffer through flows that produce the messages you need to
verify. These observations populate
`datas/proto_mapper/instancied_msg_infos.json`. Rerun the pipeline after obtaining
useful captures:

```powershell
uv run python main.py run-pipeline
```

Review `datas/protos/game_mappings_detailed.json` first to find low-confidence
mappings, messages observed at runtime, and unmatched fields. Confirm a pair only
when runtime observations, protobuf structure, and static analysis agree.

After correcting unobfuscated definitions or adding confirmed pairs, regenerate
all unobfuscated artifacts and the mapping:

```powershell
uv run python main.py synchronize-protos
```

Run this command a second time when the first pass discovers new field mappings,
so their signatures can be persisted. Nested messages or changed structures may
require a third pass. Remove incompatible signature overrides first.

Because `update-maj` resets pins, export signature overrides again after re-pinning
confirmed pairs:

```powershell
uv run python proto_mapper_assembly/scripts/export_signature_overrides.py
```

## Pinning a message pair

The interface provides the simplest method:

1. Open the account's **Debug** tab and start the sniffer.
2. Identify the obfuscated message from its content and the action context.
3. Double-click its row.
4. Choose the proposed fully qualified unobfuscated message name in the search field, then save.

The sniffer adds the pair to `datas/proto_mapper/pinned_pairs.json`. It can also
be added manually in this form:

```json
{
  "pairs": [
    {
      "obf": "hea",
      "non_obf": "Com.Ankama.Dofus.Server.Game.Protocol.GameMessage"
    }
  ]
}
```

A nested class uses its qualified name, for example `iue.iud.iuc`. Each
obfuscated and unobfuscated name may appear in only one pair.

## Pinning fields

A message pair can also enforce field mappings through
`field_mapping_by_obf`. Keys are obfuscated names and values are unobfuscated
names:

```json
{
  "pairs": [
    {
      "obf": "hea",
      "non_obf": "Com.Ankama.Dofus.Server.Game.Protocol.GameMessage",
      "field_mapping_by_obf": {
        "fllm": "request",
        "flln": "response",
        "flll": "event"
      }
    }
  ]
}
```

In a sniffer message's details, select the corresponding field in both the
**Obfuscated** and **Unobfuscated** trees, then click **Lock pinned fields**. For
message fields, the sniffer also adds the compatible child-type pair. **Show
missing fields** helps compare both structures when a capture contains only
default values.

A pin is a strong constraint, not a hypothesis. Add one only when the field's
meaning is confirmed. Fields with the same type and shape—especially multiple
`float` fields—remain ambiguous without additional evidence.

## Verifying the result

Before considering the mapping usable:

- review low-confidence entries and unmatched fields in the detailed mapping;
- replay observable actions in the sniffer and compare the obfuscated and unobfuscated trees;
- check that an obfuscated class is not already mapped before creating a new message;
- name only fields observed with a non-default value or proven by IDA tracing;
- keep `Unknown*` and `unknown_*` when the evidence is inconclusive;
- rerun `synchronize-protos` after changing definitions or pins, then review the `game_mappings*.json` diff.

The mapper can infer a child pair from a confirmed parent. This inference may
replace an inconsistent nested pin; in that case, verify the parent and field
types before forcing the child pair.

## Comparing scoring heuristics

From the repository root, run the baseline and one experimental removal in
separate processes:

```powershell
uv run python -m DBDofusUnity.proto_mapper_assembly.scripts.benchmark_cross_build --mode current --json baseline.json
uv run python -m DBDofusUnity.proto_mapper_assembly.scripts.benchmark_cross_build --mode current --without opcode_histogram --json without-opcodes.json
```

`--without` accepts multiple signals for cumulative experiments; `--help` lists
them. It changes only that benchmark process. Remaining assembly weights are
renormalized and production thresholds remain unchanged. For contributions
disabled by setting their weight to zero, preparation still runs: elapsed time
is not an estimate of the speedup from deleting their implementation.

Repeat with `--with-pins` to check the current configuration. Omit `--mode current`
to replay archives without pins or overrides. Each archive needs
`cs/Ankama.Dofus.Protocol.Game.cs`, `proto_accesses.json`, `game_mappings.json`,
and its corresponding Git history. Explicitly requested incomplete archives
fail instead of disappearing from the comparison.

Compare exact message and field outcomes per build, not just totals. The current
report includes the automatic-mode contract's required fields. Historical field
outcomes conservatively include every recorded field of the messages required by
the current automatic-mode contract; they do not prove which fields or nested messages the bot
actually exercised. Inspect nested dependencies before accepting a removal.

Field outcomes identify their reference as `pin`, `generated`, or
`historical_usage`. `unverified` means there is no reference identity to compare;
agreement with generated mappings is not independent evidence of correctness.
Preserve every previously correct required pair and introduce no new wrong or
missing required mapping. Recheck all accepted removals together. Keep a signal
when missing inputs or unverified references prevent demonstrating its removal
is safe; never compensate with additional pins.
