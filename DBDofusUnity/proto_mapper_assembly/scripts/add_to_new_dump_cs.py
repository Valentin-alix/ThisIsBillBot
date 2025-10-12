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
from collections.abc import Mapping, Sequence
from pathlib import Path

from DBDofusUnity.consts import (
    EXCLUDED_NON_OBF_FILE,
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    GAME_MAPPINGS_JSON_FILE,
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    NON_OBF_SIGNATURE_OVERRIDES_FILE,
    PINNED_PAIRS_FILE,
    PROTOS_ROOT,
)
from DBDofusUnity.proto_mapper_assembly.controllers.game_mappings import load_game_mappings_document
from DBDofusUnity.proto_mapper_assembly.controllers.message_lookup import (
    build_non_obf_alias_lookup,
    resolve_non_obf_alias,
)
from DBDofusUnity.proto_mapper_assembly.controllers.new_dump_cs import load_new_dump_cs_messages
from DBDofusUnity.proto_mapper_assembly.controllers.pinned_pairs import load_pinned_pairs, write_pinned_pairs
from DBDofusUnity.proto_mapper_assembly.controllers.signature_overrides import load_signature_overrides
from DBDofusUnity.proto_mapper_assembly.helpers.non_obf_names import build_filtered_message_namespace
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.excluded_non_obf import ExcludedNonObfConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingsDocument, SimpleGameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import SignatureOverridesFile
from DBDofusUnity.proto_mapper_assembly.parsers.dump_cs_parser import parse_messages
from DBDofusUnity.proto_mapper_assembly.parsers.protobuf_dump_cs import build_dump_cs_messages_from_pb2

_NON_OBF_PROTOS_DIR: Path = PROTOS_ROOT / "non_obf" / "game"


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


def _preserve_assembly_or_bootstrap_field_offsets(
    generated_message: DumpCSMessage,
    assembly_message: DumpCSMessage | None,
    bootstrap_message: DumpCSMessage | None,
) -> DumpCSMessage:
    """Prefer live assembly offsets and retain traced bootstrap offsets for synthetic schemas."""
    message_with_bootstrap_offsets = _preserve_existing_field_offsets(generated_message, bootstrap_message)
    return _preserve_existing_field_offsets(message_with_bootstrap_offsets, assembly_message)


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


def rebuild_new_dump_cs_from_protobufs(
    *,
    protos_dir: Path = _NON_OBF_PROTOS_DIR,
    non_obf_dump_cs_path: Path = NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    new_dump_cs_path: Path = NON_OBF_NEW_DUMP_CS_FILE,
) -> NewDumpCSFile:
    """Rebuild every non-obfuscated game descriptor while retaining known field offsets."""
    messages_by_name = build_dump_cs_messages_from_pb2(protos_dir)
    assembly_messages_by_name = {
        message.composed_name: message for message in parse_messages(str(non_obf_dump_cs_path))
    }
    bootstrap_messages_by_name = load_new_dump_cs_messages(new_dump_cs_path).root
    rebuilt_root = {
        class_name: _preserve_assembly_or_bootstrap_field_offsets(
            generated_message,
            assembly_messages_by_name.get(class_name),
            bootstrap_messages_by_name.get(class_name),
        )
        for class_name, generated_message in sorted(messages_by_name.items())
    }
    document = NewDumpCSFile(root=rebuilt_root)
    new_dump_cs_path.write_text(f"{document.model_dump_json(indent=2)}\n", encoding="utf-8")
    print(f"Rebuilt {len(rebuilt_root)} entries in {new_dump_cs_path}.")
    return document


def synchronize_non_obf_mapping_artifacts(
    *,
    protos_dir: Path = _NON_OBF_PROTOS_DIR,
    non_obf_dump_cs_path: Path = NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
    new_dump_cs_path: Path = NON_OBF_NEW_DUMP_CS_FILE,
    excluded_non_obf_path: Path = EXCLUDED_NON_OBF_FILE,
    pinned_pairs_path: Path = PINNED_PAIRS_FILE,
    signature_overrides_path: Path = NON_OBF_SIGNATURE_OVERRIDES_FILE,
    game_mappings_path: Path = GAME_MAPPINGS_JSON_FILE,
    game_mappings_detailed_path: Path = GAME_MAPPINGS_DETAILED_JSON_FILE,
) -> None:
    """Reconcile mapper artifacts with the current non-obfuscated protobuf schemas."""
    proto_messages_by_name = build_dump_cs_messages_from_pb2(protos_dir)
    rebuild_new_dump_cs_from_protobufs(
        protos_dir=protos_dir,
        non_obf_dump_cs_path=non_obf_dump_cs_path,
        new_dump_cs_path=new_dump_cs_path,
    )
    _write_automatic_exclusions(
        assembly_messages=parse_messages(str(non_obf_dump_cs_path)),
        valid_class_names=frozenset(proto_messages_by_name),
        output_path=excluded_non_obf_path,
    )
    _prune_pinned_pairs(messages_by_cls=proto_messages_by_name, path=pinned_pairs_path)
    _prune_signature_overrides(
        valid_class_names=frozenset(proto_messages_by_name), path=signature_overrides_path
    )
    _prune_game_mappings(
        proto_messages_by_name=proto_messages_by_name,
        mapping_path=game_mappings_path,
        detailed_mapping_path=game_mappings_detailed_path,
    )


def _write_automatic_exclusions(
    *,
    assembly_messages: list[DumpCSMessage],
    valid_class_names: frozenset[str],
    output_path: Path,
) -> None:
    missing_class_names = sorted(
        message.composed_name
        for message in assembly_messages
        if message.composed_name not in valid_class_names
    )
    document = ExcludedNonObfConfig(root=missing_class_names)
    output_path.write_text(f"{document.model_dump_json(indent=2)}\n", encoding="utf-8")


def _prune_pinned_pairs(*, messages_by_cls: Mapping[str, DumpCSMessage], path: Path) -> None:
    if not path.exists():
        return
    document = load_pinned_pairs(path)
    aliases_by_name, aliases_by_short_name = build_non_obf_alias_lookup(
        non_obf_messages_by_cls=messages_by_cls
    )
    retained_pairs: list[PinnedPair] = []
    for pair in document.pairs:
        try:
            resolve_non_obf_alias(
                pair.non_obf,
                aliases_by_name,
                aliases_by_short_name,
            )
        except ValueError:
            continue
        retained_pairs.append(pair)
    write_pinned_pairs(path, PinnedPairsConfig(pairs=retained_pairs))


def _prune_signature_overrides(*, valid_class_names: frozenset[str], path: Path) -> None:
    if not path.exists():
        return
    document = load_signature_overrides(path)
    pruned_root = {name: entry for name, entry in document.root.items() if name in valid_class_names}
    path.write_text(
        f"{SignatureOverridesFile(root=pruned_root).model_dump_json(indent=2)}\n", encoding="utf-8"
    )


def _prune_game_mappings(
    *,
    proto_messages_by_name: dict[str, DumpCSMessage],
    mapping_path: Path,
    detailed_mapping_path: Path,
) -> None:
    valid_mapping_keys = frozenset(
        build_filtered_message_namespace(
            is_obf=False,
            message=message,
            messages_by_cls=proto_messages_by_name,
        )
        for message in proto_messages_by_name.values()
    )
    if mapping_path.exists():
        simple_document = SimpleGameMappingsDocument.model_validate_json(
            mapping_path.read_text(encoding="utf-8")
        )
        pruned_simple = {
            name: entry for name, entry in simple_document.root.items() if name in valid_mapping_keys
        }
        mapping_path.write_text(
            f"{SimpleGameMappingsDocument(root=pruned_simple).model_dump_json(indent=2)}\n",
            encoding="utf-8",
        )
    if detailed_mapping_path.exists():
        detailed_document = load_game_mappings_document(detailed_mapping_path)
        pruned_detailed = {
            name: entry for name, entry in detailed_document.root.items() if name in valid_mapping_keys
        }
        detailed_mapping_path.write_text(
            f"{GameMappingsDocument(root=pruned_detailed).model_dump_json(indent=2)}\n",
            encoding="utf-8",
        )


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
