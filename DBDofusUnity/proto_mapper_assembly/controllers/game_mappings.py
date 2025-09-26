from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

from tqdm import tqdm

from consts import BOT_SRC_ROOT, PROTOS_ROOT
from proto_mapper_assembly.controllers.json_documents import load_root_model_or_empty
from proto_mapper_assembly.helpers.bot_usage import analyze_bot_usage, log_missing_field_mappings
from proto_mapper_assembly.helpers.non_obf_names import build_filtered_message_namespace
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.game_mappings import (
    GameMappingEntry,
    GameMappingsDocument,
    SimpleGameMappingEntry,
    SimpleGameMappingsDocument,
)
from proto_mapper_assembly.interfaces.matching import MatchResult
from proto_mapper_assembly.parsers.protobuf_dump_cs import build_dump_cs_messages_from_pb2


def build_game_mappings_document(
    matches: Sequence[MatchResult],
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
) -> GameMappingsDocument:
    generated_messages_by_cls = build_dump_cs_messages_from_pb2(PROTOS_ROOT / "non_obf")
    entries: dict[str, GameMappingEntry] = {}
    for match in tqdm(matches, "writing game mappings doc"):
        obf_message = obf_messages_by_cls.get(match.obf_signature.message_cls)
        if obf_message is None:
            message = f"Missing obfuscated dump.cs message for {match.obf_signature.message_cls}"
            raise ValueError(message)
        non_obf_message = non_obf_messages_by_cls.get(match.non_obf_signature.message_cls)
        if non_obf_message is None:
            message = f"Missing non-obfuscated dump.cs message for {match.non_obf_signature.message_cls}"
            raise ValueError(message)

        exported_non_obf_message = resolve_generated_message_alias(
            message=non_obf_message,
            generated_messages_by_cls=generated_messages_by_cls,
        )
        output_key = build_filtered_message_namespace(
            is_obf=False,
            message=exported_non_obf_message,
            messages_by_cls=generated_messages_by_cls,
        )
        if output_key in entries:
            message = f"Duplicate game mapping entry for {output_key}"
            raise ValueError(message)

        entry = GameMappingEntry(
            full_obf_msg_namespace=match.obf_signature.message_cls,
            obf_msg_namespace=build_filtered_message_namespace(
                is_obf=True, message=obf_message, messages_by_cls=obf_messages_by_cls
            ),
            full_non_obf_msg_namespace=build_full_message_namespace(exported_non_obf_message),
            field_mapping=match.field_mapping,
            field_mapping_infos=match.field_mapping_infos,
            field_mapping_rejected_infos=match.field_mapping_rejected_infos,
            field_mapping_unmapped_non_obf_fields=match.field_mapping_unmapped_non_obf_fields,
            similarity_score=match.score,
            group_similarity_score=match.group_similarity_score,
            assembly_similarity_score=match.assembly_similarity_score,
            structure_similarity_score=match.structure_similarity_score,
            runtime_confidence=match.runtime_confidence,
            match_margin=match.match_margin,
            runner_up_obf=match.runner_up_obf,
            is_low_confidence=match.is_low_confidence,
            evidence_coverage=match.evidence_coverage,
            is_runtime_observed=match.is_runtime_observed,
        )
        entries[output_key] = entry

    return GameMappingsDocument(root={message_key: entries[message_key] for message_key in sorted(entries)})


def resolve_generated_message_alias(
    *,
    message: DumpCSMessage,
    generated_messages_by_cls: dict[str, DumpCSMessage],
) -> DumpCSMessage:
    raw_namespace = build_filtered_message_namespace(
        is_obf=False, message=message, messages_by_cls=generated_messages_by_cls
    )
    generated_messages_by_namespace = {
        build_filtered_message_namespace(
            is_obf=False,
            message=generated_message,
            messages_by_cls=generated_messages_by_cls,
        ): generated_message
        for generated_message in generated_messages_by_cls.values()
    }
    if raw_namespace in generated_messages_by_namespace:
        return message

    source_fields = {field.clean_field_name for field in message.fields}
    candidates = [
        generated_message
        for generated_message in generated_messages_by_cls.values()
        if generated_message.parent_name == message.parent_name
        and {field.clean_field_name for field in generated_message.fields} == source_fields
        and (generated_message.name == message.name or generated_message.name.startswith(message.name))
    ]
    if len(candidates) == 1:
        return candidates[0]

    renamed_parent_candidates = [
        generated_message
        for generated_message in generated_messages_by_cls.values()
        if {field.clean_field_name for field in generated_message.fields} == source_fields
        and (generated_message.name == message.name or generated_message.name.startswith(message.name))
    ]
    return renamed_parent_candidates[0] if len(renamed_parent_candidates) == 1 else message


def build_full_message_namespace(message: DumpCSMessage) -> str:
    key_parts: list[str] = []
    if message.namespace is not None:
        key_parts.append(message.namespace.lower())
    if message.parent_name is not None:
        key_parts.append(message.parent_name)
    key_parts.append(message.name)
    return f".{'.'.join(key_parts)}"


def build_simple_game_mappings_document(
    detailed_document: GameMappingsDocument,
    prioritized_keys: Iterable[str] = (),
) -> SimpleGameMappingsDocument:
    prioritized_set = set(prioritized_keys)
    sorted_items = sorted(detailed_document.root.items())

    bot_items: list[tuple[str, GameMappingEntry]] = []
    rest_items: list[tuple[str, GameMappingEntry]] = []
    for message_key, entry in sorted_items:
        target = bot_items if message_key in prioritized_set else rest_items
        target.append((message_key, entry))

    ordered = {
        message_key: SimpleGameMappingEntry(
            obf_msg_namespace=entry.obf_msg_namespace,
            field_mapping=entry.field_mapping,
        )
        for message_key, entry in (*bot_items, *rest_items)
    }
    return SimpleGameMappingsDocument(root=ordered)


def validate_game_mapping_targets(document: GameMappingsDocument) -> None:
    generated_messages_by_cls = build_dump_cs_messages_from_pb2(PROTOS_ROOT / "non_obf")
    canonical_targets = {
        build_filtered_message_namespace(
            is_obf=False,
            message=message,
            messages_by_cls=generated_messages_by_cls,
        )
        for message in generated_messages_by_cls.values()
    }
    invalid_targets = sorted(set(document.root) - canonical_targets)
    if invalid_targets:
        message = "Game mapping targets missing from generated protobuf descriptors:\n  " + "\n  ".join(
            invalid_targets
        )
        raise ValueError(message)


def write_game_mappings(
    matches: Sequence[MatchResult],
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    output_path: Path,
    detailed_output_path: Path,
) -> None:
    detailed_document = build_game_mappings_document(
        matches,
        obf_messages_by_cls=obf_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
    )
    validate_game_mapping_targets(detailed_document)
    bot_usage = analyze_bot_usage(non_obf_messages_by_cls, BOT_SRC_ROOT)
    bot_used_json_keys = {
        build_filtered_message_namespace(
            is_obf=False,
            message=non_obf_messages_by_cls[composed],
            messages_by_cls=non_obf_messages_by_cls,
        )
        for composed in bot_usage.bot_used_messages
        if composed in non_obf_messages_by_cls
    }
    simple_document = build_simple_game_mappings_document(
        detailed_document, prioritized_keys=bot_used_json_keys
    )
    detailed_output_path.write_text(f"{detailed_document.model_dump_json(indent=2)}\n", encoding="utf-8")
    output_path.write_text(f"{simple_document.model_dump_json(indent=2)}\n", encoding="utf-8")
    log_missing_field_mappings(bot_usage, matches, non_obf_messages_by_cls)


def load_game_mappings_document(path: Path) -> GameMappingsDocument:
    return load_root_model_or_empty(path, GameMappingsDocument)
