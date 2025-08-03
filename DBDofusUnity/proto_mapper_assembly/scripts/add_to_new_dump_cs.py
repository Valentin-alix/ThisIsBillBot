r"""
Add or update entries in `new_dump_cs.json` from non-obfuscated protobuf descriptors.

Reads message descriptors from the generated `_pb2.py` modules under
`datas/protos/non_obf/`, converts each requested class to a `DumpCSMessage`
and overwrites the matching entry in `new_dump_cs.json`. Existing fields keep
their memory offsets from `Ankama.Dofus.Protocol.Game.cs`; protobuf-only new
fields keep offset 0 until traced/regenerated data exists for them.

Usage:
    uv run python proto_mapper_assembly/scripts/add_to_new_dump_cs.py \
        <composed_class_name>... [--dry-run]

`<composed_class_name>` is the `new_dump_cs.json` key form, e.g.:
    Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightLiveStateEvent
    FightLiveStateEvent.Types.FightEntityState
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from consts import PROJECT_ROOT

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from consts import (
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    PROTOS_ROOT,
)
from proto_mapper_assembly.controllers.game_mappings import load_game_mappings_document
from proto_mapper_assembly.controllers.new_dump_cs import load_new_dump_cs_messages
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile
from proto_mapper_assembly.parsers.dump_cs_parser import parse_messages
from proto_mapper_assembly.parsers.protobuf_dump_cs import build_dump_cs_messages_from_pb2

_NON_OBF_PROTOS_DIR: Path = PROTOS_ROOT / "non_obf"


def _preserve_existing_field_offsets(
    generated_message: DumpCSMessage,
    existing_message: DumpCSMessage | None,
) -> DumpCSMessage:
    if existing_message is None:
        return generated_message
    existing_offsets_by_field_name = _build_existing_offset_lookup(existing_message.fields)
    merged_fields = [
        _copy_existing_offset(field, existing_offsets_by_field_name) for field in generated_message.fields
    ]
    return generated_message.model_copy(update={"fields": merged_fields})


def _build_existing_offset_lookup(fields: list[DumpCSMessageField]) -> dict[str, int]:
    offsets_by_field_name: dict[str, int] = {}
    for field in fields:
        offsets_by_field_name.setdefault(field.clean_field_name, field.memory_offset)
        if field.property_name is not None:
            offsets_by_field_name.setdefault(field.property_name, field.memory_offset)
    return offsets_by_field_name


def _copy_existing_offset(
    generated_field: DumpCSMessageField,
    existing_offsets_by_field_name: dict[str, int],
) -> DumpCSMessageField:
    memory_offset = existing_offsets_by_field_name.get(generated_field.clean_field_name)
    if memory_offset is None and generated_field.property_name is not None:
        memory_offset = existing_offsets_by_field_name.get(generated_field.property_name)
    if memory_offset is None:
        return generated_field
    return generated_field.model_copy(update={"memory_offset": memory_offset})


def check_nesting_matches_obfuscated_side(
    message: DumpCSMessage,
    *,
    game_mappings_path: Path = GAME_MAPPINGS_DETAILED_JSON_FILE,
) -> str | None:
    if message.parent_name is not None or not game_mappings_path.exists():
        return None
    mappings = load_game_mappings_document(game_mappings_path)
    for entry in mappings.root.values():
        if entry.full_non_obf_msg_namespace.split(".")[-1] != message.name:
            continue
        if "." not in entry.obf_msg_namespace:
            return None
        return (
            f"{message.name} is declared at top level in the .proto, but it is mapped to the nested "
            f"obfuscated class {entry.obf_msg_namespace!r}. build_static_score_data skips pairs whose "
            f"is_root_msg disagree, so this message would never be scored. Nest it under its parent "
            f"message in the .proto, regenerate the _pb2, and add it as <Parent>.Types.{message.name}."
        )
    return None


def build_new_dump_cs_entries(
    class_names: Sequence[str],
    *,
    protos_dir: Path = _NON_OBF_PROTOS_DIR,
    non_obf_dump_cs_path: Path = NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    new_dump_cs_path: Path = NON_OBF_NEW_DUMP_CS_FILE,
) -> NewDumpCSFile:
    messages_by_name = build_dump_cs_messages_from_pb2(protos_dir)
    existing_messages_by_name = {
        message.composed_name: message for message in parse_messages(str(non_obf_dump_cs_path))
    }

    document = load_new_dump_cs_messages(new_dump_cs_path)
    updated_root = dict(document.root)

    for class_name in class_names:
        message = messages_by_name.get(class_name)
        if message is None:
            available = "\n  ".join(sorted(messages_by_name)[:10])
            err = f"No protobuf descriptor found for {class_name!r}. First few known names:\n  {available}"
            raise SystemExit(err)

        updated_root[class_name] = _preserve_existing_field_offsets(
            message,
            existing_messages_by_name.get(class_name),
        )
        warning = check_nesting_matches_obfuscated_side(message)
        if warning is not None:
            print(f"WARNING: {warning}")
        print(f"Built entry for {class_name} ({len(message.fields)} fields).")

    new_document = NewDumpCSFile(root=updated_root)
    new_dump_cs_path.write_text(new_document.model_dump_json(indent=2), encoding="utf-8")
    print(f"Written {len(updated_root)} entries to {new_dump_cs_path}.")
    return new_document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "class_names",
        nargs="+",
        help="Composed C# class names to add/overwrite (new_dump_cs.json keys).",
    )
    # (example : Com.Ankama.Dofus.Server.Game.Protocol.Fight.Preparation.FightPreparationEnterRequest)
    args = parser.parse_args()
    build_new_dump_cs_entries(args.class_names)


if __name__ == "__main__":
    main()
