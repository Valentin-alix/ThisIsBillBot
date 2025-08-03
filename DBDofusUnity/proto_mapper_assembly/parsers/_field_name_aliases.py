from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty


def get_property_name_by_field_name(
    fields: list[DumpCSMessageField],
    properties: list[DumpCSMessageProperty],
) -> dict[str, str]:
    property_name_map: dict[str, str] = {}
    used_property_names: set[str] = set()
    property_types_by_name = {
        property_entry.property_name: property_entry.normalized_type for property_entry in properties
    }

    for field in fields:
        explicit_property_name = _get_suffix_based_property_name(field, property_types_by_name)
        if explicit_property_name is None:
            continue
        property_name_map[field.field_name] = explicit_property_name
        used_property_names.add(explicit_property_name)

    remaining_properties = [
        property_entry
        for property_entry in properties
        if property_entry.property_name not in used_property_names
    ]
    consumed_indices: set[int] = set()

    for field in fields:
        if field.field_name in property_name_map:
            continue
        if not field.is_proto_field and not field.field_name.startswith("_"):
            continue
        for i, property_candidate in enumerate(remaining_properties):
            if i in consumed_indices:
                continue
            if property_candidate.normalized_type != field.normalized_type:
                continue
            property_name_map[field.field_name] = property_candidate.property_name
            consumed_indices.add(i)
            break

    return property_name_map


def _get_suffix_based_property_name(
    field: DumpCSMessageField,
    property_types_by_name: dict[str, str],
) -> str | None:
    if not field.field_name.endswith("_") or field.field_name.startswith("_"):
        return None
    base_name = field.field_name[:-1]
    if not base_name:
        return None
    property_name = f"{base_name[0].upper()}{base_name[1:]}"
    property_type = property_types_by_name.get(property_name)
    if property_type != field.normalized_type:
        return None
    return property_name
