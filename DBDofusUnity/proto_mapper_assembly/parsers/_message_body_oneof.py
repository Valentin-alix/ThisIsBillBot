from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.parsers._message_body_scan import _extract_enum_type_fields
from proto_mapper_assembly.parsers.clr_types import categorize_field


@dataclass(frozen=True, slots=True)
class _PositionedOneofBackingField:
    position: int
    field: DumpCSMessageField


def build_synthetic_oneof_fields(
    *,
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
    property_positions_by_name: dict[str, int],
    field_positions_by_name: dict[str, int],
    enum_names: frozenset[str],
) -> list[DumpCSMessageField]:
    """Build all fields that are part of a oneof from oneof backing fields."""
    oneof_backing_fields = _get_oneof_backing_fields(fields, field_positions_by_name)
    if not oneof_backing_fields:
        return []

    already_mapped_property_names = {
        field.property_name for field in fields if field.property_name is not None
    }
    return _build_synthetic_oneof_fields(
        properties=properties,
        property_positions_by_name=property_positions_by_name,
        mapped_property_names=already_mapped_property_names,
        oneof_backing_fields=oneof_backing_fields,
        enum_names=enum_names,
    )


def _get_oneof_backing_fields(
    fields: list[DumpCSMessageField],
    field_positions_by_name: dict[str, int],
) -> list[_PositionedOneofBackingField]:
    return sorted(
        [
            _PositionedOneofBackingField(
                position=field_positions_by_name[field.field_name],
                field=field,
            )
            for field in fields
            if field.category == FieldCategoryEnum.ONEOF and field.field_name in field_positions_by_name
        ],
        key=lambda positioned_field: positioned_field.position,
    )


def _build_synthetic_oneof_fields(
    *,
    properties: list[DumpCSMessageProperty],
    property_positions_by_name: dict[str, int],
    mapped_property_names: set[str],
    oneof_backing_fields: list[_PositionedOneofBackingField],
    enum_names: frozenset[str],
) -> list[DumpCSMessageField]:
    fallback_fields: list[DumpCSMessageField] = []
    properties_by_backing_field = _build_properties_by_backing_field(
        properties=properties,
        property_positions_by_name=property_positions_by_name,
        mapped_property_names=mapped_property_names,
        oneof_backing_fields=oneof_backing_fields,
    )
    for backing_field in oneof_backing_fields:
        grouped_properties = properties_by_backing_field[backing_field.field.field_name]
        for fallback_index, property_entry in enumerate(grouped_properties):
            fallback_order = 10_000 + fallback_index
            fallback_fields.append(
                _build_synthetic_oneof_field(
                    property_entry,
                    backing_field.field,
                    fallback_order,
                    enum_names,
                )
            )
    return fallback_fields


def _build_properties_by_backing_field(
    *,
    properties: list[DumpCSMessageProperty],
    property_positions_by_name: dict[str, int],
    mapped_property_names: set[str],
    oneof_backing_fields: list[_PositionedOneofBackingField],
) -> dict[str, list[DumpCSMessageProperty]]:
    properties_by_backing_field: dict[str, list[DumpCSMessageProperty]] = {}
    backing_positions = [backing_field.position for backing_field in oneof_backing_fields]
    for backing_field in oneof_backing_fields:
        properties_by_backing_field[backing_field.field.field_name] = []

    positioned_properties = sorted(
        [
            _PositionedProperty(
                position=property_positions_by_name[property_entry.property_name],
                property_entry=property_entry,
            )
            for property_entry in properties
            if property_entry.property_name not in mapped_property_names
            and property_entry.property_name in property_positions_by_name
        ],
        key=_get_positioned_property_sort_key,
    )

    for positioned_property in positioned_properties:
        backing_field_index = bisect_right(backing_positions, positioned_property.position) - 1
        backing_field_index = max(backing_field_index, 0)
        backing_field = oneof_backing_fields[backing_field_index].field.field_name
        properties_by_backing_field[backing_field].append(positioned_property.property_entry)
    return properties_by_backing_field


@dataclass(frozen=True, slots=True)
class _PositionedProperty:
    position: int
    property_entry: DumpCSMessageProperty


def _get_positioned_property_sort_key(positioned_property: _PositionedProperty) -> tuple[int, str]:
    return positioned_property.position, positioned_property.property_entry.property_name


def _build_synthetic_oneof_field(
    property_entry: DumpCSMessageProperty,
    backing_field: DumpCSMessageField,
    decl_order: int,
    enum_names: frozenset[str],
) -> DumpCSMessageField:
    enum_key_type, enum_value_type = _extract_enum_type_fields(property_entry.normalized_type, enum_names)
    return DumpCSMessageField(
        clr_type=property_entry.clr_type,
        normalized_type=property_entry.normalized_type,
        category=categorize_field(property_entry.clr_type, enum_names),
        memory_offset=backing_field.memory_offset,
        field_name=property_entry.property_name,
        property_name=property_entry.property_name,
        proto_decl_order=decl_order,
        oneof_group_name=backing_field.field_name.rstrip("_"),
        is_synthetic_oneof_variant=True,
        enum_key_type=enum_key_type,
        enum_value_type=enum_value_type,
    )
