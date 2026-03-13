from collections.abc import Sequence

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import FieldAccessEntry, FieldAccessSignatures
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import (
    DumpCSMessage,
    DumpCSMessageField,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.message_field_resolution_lookup import MessageFieldResolutionLookup


def build_message_field_resolution_lookup(
    messages: Sequence[DumpCSMessage],
) -> dict[str, MessageFieldResolutionLookup]:
    return {message.composed_name: build_field_resolution_lookup(message) for message in messages}


def build_field_resolution_lookup(message: DumpCSMessage) -> MessageFieldResolutionLookup:
    return MessageFieldResolutionLookup(fields=message.fields)


def build_dump_cs_field_lookup(message: DumpCSMessage) -> dict[str, DumpCSMessageField]:
    lookup = build_field_resolution_lookup(message)
    return {**lookup.by_clean_name, **lookup.by_property_name}


def resolve_field_by_access_entry(
    access: FieldAccessEntry,
    field_resolution_by_message_cls: dict[str, MessageFieldResolutionLookup],
) -> DumpCSMessageField:
    field_resolution = field_resolution_by_message_cls[access.cls]
    if access.property_name is not None:
        by_property_name = field_resolution.by_property_name.get(access.property_name)
        if by_property_name is not None:
            return by_property_name
        error = f"Cannot resolve property access {access.cls}.{access.property_name}"
        raise KeyError(error)

    assert access.field_offset is not None, "offset-based field access requires field_offset"
    return field_resolution.by_instance_offset[access.field_offset]


def bind_field_signatures_to_message_fields(
    *,
    field_signatures: Sequence[FieldAccessSignatures],
    message: DumpCSMessage,
) -> list[FieldAccessSignatures]:
    lookup = build_field_resolution_lookup(message)

    result: list[FieldAccessSignatures] = []
    for field_signature in field_signatures:
        keyed_field = lookup.by_field_key.get(field_signature.field_key)
        if keyed_field is not None:
            result.append(field_signature)
            continue

        offset_candidates = [
            field
            for field in lookup.by_offset.get(field_signature.field_offset, ())
            if field.field_type_shape == field_signature.field_type_shape
        ]
        if len(offset_candidates) != 1:
            message_text = (
                f"Cannot bind field signature at offset {field_signature.field_offset} "
                f"to message {message.composed_name}"
            )
            raise ValueError(message_text)
        resolved_field = offset_candidates[0]
        result.append(field_signature.model_copy(update={"field_key": resolved_field.field_key}))
    return result
