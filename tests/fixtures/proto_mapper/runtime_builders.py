from __future__ import annotations

from collections.abc import Mapping

from tests.fixtures.proto_mapper.message_builders import message_signature

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import FieldMappingResult
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import (
    MessageRuntimeMetadata,
    RuntimeRemappingContext,
    RuntimeValidationCandidate,
)


def runtime_entry(
    payload: Mapping[str, object],
    *,
    from_server: bool = False,
    is_root_msg: bool = True,
    is_game_msg: bool = False,
    capture_sequence: int | None = 0,
    capture_session_id: str | None = None,
) -> dict[str, object]:
    entry = dict(payload)
    entry["from_server"] = from_server
    entry["is_root_msg"] = is_root_msg
    entry["is_game_msg"] = is_game_msg
    entry["capture_sequence"] = capture_sequence
    if capture_session_id is not None:
        entry["capture_session_id"] = capture_session_id
    return entry


def make_candidate(
    obf_msg: DumpCSMessage,
    non_obf_msg: DumpCSMessage,
    field_mapping: dict[str, str],
) -> RuntimeValidationCandidate:
    return RuntimeValidationCandidate(
        obf_msg_sig=message_signature(obf_msg.name, [], dump_cs_msg=obf_msg),
        non_obf_msg_sig=message_signature(non_obf_msg.name, [], dump_cs_msg=non_obf_msg),
        obf_index=0,
        non_obf_index=0,
        field_mapping_result=FieldMappingResult(
            field_mapping=field_mapping,
            has_validation_failure=False,
            field_mapping_infos={},
            discovered_message_matches=(),
            field_mapping_rejected_infos={},
            field_mapping_unmapped_non_obf_fields={},
        ),
    )


def make_simple_context(
    obf_msg: DumpCSMessage,
    non_obf_msg: DumpCSMessage,
    obf_live_fields: dict[str, DumpCSMessageField],
    non_obf_live_fields: dict[str, DumpCSMessageField],
    obf_child_cls_by_key: dict[FieldKey, str | None] | None = None,
    non_obf_child_cls_by_key: dict[FieldKey, str | None] | None = None,
    candidates_by_non_obf: dict[str, dict[str, RuntimeValidationCandidate]] | None = None,
    extra_obf_metadata: dict[str, MessageRuntimeMetadata] | None = None,
    extra_non_obf_metadata: dict[str, MessageRuntimeMetadata] | None = None,
) -> RuntimeRemappingContext:
    obf_metadata = MessageRuntimeMetadata(
        live_runtime_fields_by_name=obf_live_fields,
        child_message_cls_by_field_key=obf_child_cls_by_key or {},
    )
    non_obf_metadata = MessageRuntimeMetadata(
        live_runtime_fields_by_name=non_obf_live_fields,
        child_message_cls_by_field_key=non_obf_child_cls_by_key or {},
    )
    all_obf_meta: dict[str, MessageRuntimeMetadata] = {obf_msg.name: obf_metadata}
    all_non_obf_meta: dict[str, MessageRuntimeMetadata] = {non_obf_msg.name: non_obf_metadata}
    if extra_obf_metadata:
        all_obf_meta.update(extra_obf_metadata)
    if extra_non_obf_metadata:
        all_non_obf_meta.update(extra_non_obf_metadata)

    return RuntimeRemappingContext(
        candidates_by_non_obf=candidates_by_non_obf or {},
        obf_messages_by_cls={obf_msg.name: obf_msg},
        non_obf_messages_by_cls={non_obf_msg.name: non_obf_msg},
        get_obf_metadata=lambda msg: all_obf_meta[msg.name],
        get_non_obf_metadata=lambda msg: all_non_obf_meta[msg.name],
        resolve_field_mapping_by_pair=lambda _obf, _non_obf: {},
    )
