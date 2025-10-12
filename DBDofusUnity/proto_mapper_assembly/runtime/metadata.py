from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.helpers.proto_helpers import resolve_child_message_cls
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import MessageRuntimeMetadata


def build_message_runtime_metadata(
    *,
    message: DumpCSMessage,
    messages_by_cls: dict[str, DumpCSMessage],
    type_index: dict[str, tuple[DumpCSMessage, ...]],
    live_field_keys: frozenset[FieldKey] | None,
) -> MessageRuntimeMetadata:
    runtime_fields_by_name = _build_runtime_field_lookup(message)
    live_runtime_fields_by_name = {
        field_name: field
        for field_name, field in runtime_fields_by_name.items()
        if live_field_keys is None or field.field_key in live_field_keys
    }
    child_message_cls_by_field_key = {
        field.field_key: resolve_child_message_cls(
            field=field,
            parent_message=message,
            messages_by_cls=messages_by_cls,
            type_index=type_index,
        )
        for field in runtime_fields_by_name.values()
    }
    return MessageRuntimeMetadata(
        live_runtime_fields_by_name=live_runtime_fields_by_name,
        child_message_cls_by_field_key=child_message_cls_by_field_key,
    )


def _build_runtime_field_lookup(message: DumpCSMessage) -> dict[str, DumpCSMessageField]:
    return {
        field.clean_field_name: field
        for field in message.fields
        if field.is_declared_proto_shape_field and field.property_name is not None
    }
