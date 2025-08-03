from __future__ import annotations

from collections import defaultdict
from functools import cache
from typing import NamedTuple

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField
from proto_mapper_assembly.interfaces.field_category import (
    FieldCategoryEnum,
    FieldTypeLeafKind,
)
from proto_mapper_assembly.parsers._clr_type_utils import extract_map_inner_types, extract_repeated_inner_type
from proto_mapper_assembly.parsers.clr_types import resolve_non_container_field_kind


class TypeIndexKey(NamedTuple):
    composed_name: str
    short_name: str


@cache
def _build_type_index_from_keys(
    message_keys: tuple[TypeIndexKey, ...],
) -> dict[str, tuple[str, ...]]:
    grouped_messages: dict[str, list[str]] = defaultdict(list)
    for composed_name, short_name in message_keys:
        grouped_messages[short_name].append(composed_name)
    return {
        short_name: tuple(sorted(composed_names)) for short_name, composed_names in grouped_messages.items()
    }


def build_types_by_short_name(
    messages_by_cls: dict[str, DumpCSMessage],
) -> dict[str, tuple[DumpCSMessage, ...]]:
    message_keys = tuple(
        TypeIndexKey(message.composed_name, message.name) for message in messages_by_cls.values()
    )
    indexed_names = _build_type_index_from_keys(message_keys)
    return {
        short_name: tuple(messages_by_cls[composed_name] for composed_name in composed_names)
        for short_name, composed_names in indexed_names.items()
    }


def extract_child_type_name(field: DumpCSMessageField) -> str | None:
    if field.category == FieldCategoryEnum.MESSAGE:
        return field.normalized_type
    if field.category == FieldCategoryEnum.REPEATED:
        repeated_inner_type = extract_repeated_inner_type(field.normalized_type)
        if repeated_inner_type is None:
            return None
        inner_category = resolve_non_container_field_kind(
            repeated_inner_type, field.enum_key_type, field.enum_value_type
        )
        return repeated_inner_type if inner_category == FieldTypeLeafKind.MESSAGE else None
    if field.category == FieldCategoryEnum.MAP:
        map_inner_types = extract_map_inner_types(field.normalized_type)
        if map_inner_types is None:
            return None
        inner_category = resolve_non_container_field_kind(
            map_inner_types[1], field.enum_key_type, field.enum_value_type
        )
        return map_inner_types[1] if inner_category == FieldTypeLeafKind.MESSAGE else None
    return None


def resolve_child_message_cls(
    *,
    field: DumpCSMessageField,
    parent_message: DumpCSMessage,
    messages_by_cls: dict[str, DumpCSMessage],
    type_index: dict[str, tuple[DumpCSMessage, ...]],
) -> str | None:
    child_type = extract_child_type_name(field)
    if child_type is None:
        return None
    return resolve_message_cls(
        type_name=child_type,
        parent_message=parent_message,
        messages_by_cls=messages_by_cls,
        type_index=type_index,
    )


def resolve_message_cls(
    *,
    type_name: str,
    parent_message: DumpCSMessage,
    messages_by_cls: dict[str, DumpCSMessage],
    type_index: dict[str, tuple[DumpCSMessage, ...]],
) -> str | None:
    candidate_names = [type_name]
    if parent_message.namespace is not None:
        candidate_names.append(f"{parent_message.namespace}.{type_name}")
    if parent_message.parent_name is not None:
        candidate_names.append(f"{parent_message.parent_name}.{type_name}")

    for candidate_name in candidate_names:
        if candidate_name in messages_by_cls:
            return candidate_name

    short_name = type_name.rsplit(".", maxsplit=1)[-1]
    candidates = list(type_index.get(short_name, ()))
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0].composed_name

    namespace_candidates = [
        candidate
        for candidate in candidates
        if candidate.namespace is not None and candidate.namespace == parent_message.namespace
    ]
    if len(namespace_candidates) == 1:
        return namespace_candidates[0].composed_name

    parent_candidates = [
        candidate
        for candidate in candidates
        if candidate.parent_name is not None and candidate.parent_name == parent_message.parent_name
    ]
    if len(parent_candidates) == 1:
        return parent_candidates[0].composed_name

    return None
