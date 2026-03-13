from DBDofusUnity.proto_mapper_assembly.helpers.proto_helpers import resolve_child_message_cls
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import FieldAccessSignatures, MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import (
    FieldMappingContext,
    MatchingStoreProtocol,
    MessageSideData,
    PreparedFieldMappingContext,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_field_validation import (
    collect_runtime_alive_field_names,
    collect_validated_field_names,
)


def prepare_field_mapping_context(
    *,
    non_obf_signature: MessageAccessSignature,
    obf_signature: MessageAccessSignature,
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    obf_messages_by_cls: dict[str, DumpCSMessage],
    matching_store: MatchingStoreProtocol | None,
    field_mapping_context: FieldMappingContext,
    obf_type_index: dict[str, tuple[DumpCSMessage, ...]],
    non_obf_type_index: dict[str, tuple[DumpCSMessage, ...]],
    pinned_pair: PinnedPair | None,
) -> PreparedFieldMappingContext:
    forced_non_obf_field_names = _build_forced_non_obf_field_names(
        pinned_pair=pinned_pair,
        non_obf_signature=non_obf_signature,
    )
    forced_obf_field_names = _build_forced_obf_field_names(
        pinned_pair=pinned_pair,
        obf_signature=obf_signature,
        obf_messages_by_cls=obf_messages_by_cls,
        field_mapping_context=field_mapping_context,
    )

    non_obf_fields = non_obf_signature.get_exportable_fields(forced_field_names=forced_non_obf_field_names)
    obf_fields = obf_signature.get_exportable_fields(forced_field_names=forced_obf_field_names)
    non_obf_field_signature_by_field_key = build_prepared_field_signature_by_field_key(
        signature=non_obf_signature,
        fields=non_obf_fields,
    )
    obf_field_signature_by_field_key = build_prepared_field_signature_by_field_key(
        signature=obf_signature,
        fields=obf_fields,
    )

    return PreparedFieldMappingContext(
        non_obf_signature=non_obf_signature,
        obf_signature=obf_signature,
        non_obf=MessageSideData(
            messages_by_cls=non_obf_messages_by_cls,
            type_index=non_obf_type_index,
            fields=non_obf_fields,
            field_signature_by_field_key=non_obf_field_signature_by_field_key,
            child_cls_by_field_key=build_child_message_cls_by_field_key(
                fields=non_obf_fields,
                parent_message=non_obf_signature.dump_cs_msg,
                messages_by_cls=non_obf_messages_by_cls,
                type_index=non_obf_type_index,
            ),
        ),
        obf=MessageSideData(
            messages_by_cls=obf_messages_by_cls,
            type_index=obf_type_index,
            fields=obf_fields,
            field_signature_by_field_key=obf_field_signature_by_field_key,
            child_cls_by_field_key=build_child_message_cls_by_field_key(
                fields=obf_fields,
                parent_message=obf_signature.dump_cs_msg,
                messages_by_cls=obf_messages_by_cls,
                type_index=obf_type_index,
            ),
        ),
        matching_store=matching_store,
        field_mapping_context=field_mapping_context,
        pinned_pair=pinned_pair,
    )


def build_prepared_field_signature_by_field_key(
    *,
    signature: MessageAccessSignature,
    fields: tuple[DumpCSMessageField, ...],
) -> dict[FieldKey, FieldAccessSignatures]:
    field_signatures_by_key = dict(signature.field_signature_by_field_key)
    for field in fields:
        field_key = field.field_key
        if field_key in field_signatures_by_key:
            continue
        field_signatures_by_key[field_key] = _build_field_access_signature_from_field(field)
    return field_signatures_by_key


def build_child_message_cls_by_field_key(
    *,
    fields: tuple[DumpCSMessageField, ...],
    parent_message: DumpCSMessage,
    messages_by_cls: dict[str, DumpCSMessage],
    type_index: dict[str, tuple[DumpCSMessage, ...]],
) -> dict[FieldKey, str | None]:
    child_cls_by_field_key: dict[FieldKey, str | None] = {}
    for field in fields:
        field_key = field.field_key
        child_cls_by_field_key[field_key] = resolve_child_message_cls(
            field=field,
            parent_message=parent_message,
            messages_by_cls=messages_by_cls,
            type_index=type_index,
        )
    return child_cls_by_field_key


def _build_forced_non_obf_field_names(
    *,
    pinned_pair: PinnedPair | None,
    non_obf_signature: MessageAccessSignature,
) -> frozenset[str]:
    forced_field_names = set[str]()
    if pinned_pair is not None:
        forced_field_names.update(pinned_pair.field_mapping_by_obf.values())
    forced_field_names.update(collect_validated_field_names(non_obf_signature.dump_cs_msg.name))
    return frozenset(forced_field_names)


def _build_forced_obf_field_names(
    *,
    pinned_pair: PinnedPair | None,
    obf_signature: MessageAccessSignature,
    obf_messages_by_cls: dict[str, DumpCSMessage],
    field_mapping_context: FieldMappingContext,
) -> frozenset[str]:
    forced_field_names: set[str] = set()
    if pinned_pair is not None:
        forced_field_names.update(pinned_pair.field_mapping_by_obf)

    runtime_instances = field_mapping_context.runtime_data_store.get_normalized_content_for_obf_message(
        message=obf_signature.dump_cs_msg,
        obf_messages_by_cls=obf_messages_by_cls,
    )
    forced_field_names.update(collect_runtime_alive_field_names(runtime_instances))
    return frozenset(forced_field_names)


def _build_field_access_signature_from_field(field: DumpCSMessageField) -> FieldAccessSignatures:
    return FieldAccessSignatures(
        field_key=field.field_key,
        field_type_shape=field.field_type_shape,
        accesses=[],
        is_traced=False,
    )
