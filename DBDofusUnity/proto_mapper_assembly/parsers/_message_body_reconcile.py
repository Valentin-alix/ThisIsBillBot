from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers._field_name_aliases import get_property_name_by_field_name
from DBDofusUnity.proto_mapper_assembly.parsers._message_body_scan import (
    _ExcludedBooleanProperty,
)


def reconcile_message_body(
    *,
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
    excluded_boolean_properties: list[_ExcludedBooleanProperty],
    const_int_positions: list[int],
    field_positions_by_name: dict[str, int],
) -> None:
    _mark_obfuscated_presence_backing_fields(
        fields,
        properties,
        excluded_boolean_properties,
        const_int_positions,
        field_positions_by_name,
    )
    _assign_field_properties(fields, properties)


def _mark_obfuscated_presence_backing_fields(
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
    excluded_boolean_properties: list[_ExcludedBooleanProperty],
    const_int_positions: list[int],
    field_positions_by_name: dict[str, int],
) -> None:
    if len(excluded_boolean_properties) == 0 or len(const_int_positions) == 0:
        return

    current_mapping = get_property_name_by_field_name(fields, properties)
    has_complete_ordered_mapping = _is_complete_ordered_mapping(fields, properties, current_mapping)
    if has_complete_ordered_mapping:
        if _count_instance_proto_fields(fields) <= len(properties):
            return
        matching_candidates = [
            field
            for field in fields
            if _is_premapped_hasbits_candidate(
                field, current_mapping, field_positions_by_name, const_int_positions
            )
            and _candidate_restores_complete_mapping(field, fields, properties)
        ]
        if len(matching_candidates) == 1:
            matching_candidates[0].is_proto_field = False
        return

    matching_candidates = [
        field
        for field in fields
        if _is_obfuscated_presence_candidate(
            field,
            current_mapping,
            field_positions_by_name,
            fields,
            const_int_positions,
        )
        and _candidate_restores_complete_mapping(field, fields, properties)
    ]
    if len(matching_candidates) != 1:
        matching_candidates = [
            field
            for field in fields
            if _is_premapped_hasbits_candidate(
                field, current_mapping, field_positions_by_name, const_int_positions
            )
            and _candidate_restores_complete_mapping(field, fields, properties)
        ]
    if len(matching_candidates) != 1:
        return
    matching_candidates[0].is_proto_field = False


def _is_complete_ordered_mapping(
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
    field_property_name_map: dict[str, str],
) -> bool:
    if len(field_property_name_map) != len(properties):
        return False
    mapped_property_names = [
        field_property_name_map[field.field_name]
        for field in fields
        if field.field_name in field_property_name_map and field.is_proto_field
    ]
    return mapped_property_names == [property_entry.property_name for property_entry in properties]


def _count_instance_proto_fields(fields: list[DumpCSMessageField]) -> int:
    return sum(1 for field in fields if field.is_instance_backed_proto_field)


def _is_obfuscated_presence_candidate(
    field: DumpCSMessageField,
    current_mapping: dict[str, str],
    field_positions_by_name: dict[str, int],
    fields: list[DumpCSMessageField],
    const_int_positions: list[int],
) -> bool:
    if not field.is_proto_field:
        return False
    if field.field_name in current_mapping:
        return False
    if field.normalized_type != "int":
        return False

    field_position = field_positions_by_name.get(field.field_name)
    if field_position is None:
        return False
    interval_fields = _get_fields_in_const_interval(
        field_position,
        fields,
        field_positions_by_name,
        const_int_positions,
    )
    if len(interval_fields) == 0:
        return False
    return interval_fields[0].category != FieldCategoryEnum.ONEOF


def _candidate_restores_complete_mapping(
    candidate_field: DumpCSMessageField,
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
) -> bool:
    candidate_mapping = get_property_name_by_field_name(
        [
            current_field.model_copy(update={"is_proto_field": False})
            if current_field.field_name == candidate_field.field_name
            else current_field
            for current_field in fields
        ],
        properties,
    )
    return _is_complete_ordered_mapping(fields, properties, candidate_mapping)


def _get_fields_in_const_interval(
    field_position: int,
    fields: list[DumpCSMessageField],
    field_positions_by_name: dict[str, int],
    const_int_positions: list[int],
) -> list[DumpCSMessageField]:
    lower_bound: int | None = None
    upper_bound: int | None = None
    for position in const_int_positions:
        if position < field_position:
            lower_bound = position
            continue
        upper_bound = position
        break
    return [
        field
        for field in fields
        if (
            (current_position := field_positions_by_name.get(field.field_name)) is not None
            and (lower_bound is None or current_position > lower_bound)
            and (upper_bound is None or current_position < upper_bound)
        )
    ]


def _is_premapped_hasbits_candidate(
    field: DumpCSMessageField,
    current_mapping: dict[str, str],
    field_positions_by_name: dict[str, int],
    const_int_positions: list[int],
) -> bool:
    if not field.is_proto_field:
        return False
    if field.field_name not in current_mapping:
        return False
    if field.normalized_type != "int":
        return False
    field_position = field_positions_by_name.get(field.field_name)
    if field_position is None:
        return False
    return not any(position < field_position for position in const_int_positions)


def _assign_field_properties(
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
) -> None:
    field_property_name_map = get_property_name_by_field_name(fields, properties)
    for field in fields:
        property_name = field_property_name_map.get(field.field_name)
        if property_name is None:
            continue
        field.property_name = property_name
