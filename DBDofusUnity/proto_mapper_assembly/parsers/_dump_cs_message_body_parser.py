from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty
from proto_mapper_assembly.parsers._message_body_oneof import build_synthetic_oneof_fields
from proto_mapper_assembly.parsers._message_body_reconcile import reconcile_message_body
from proto_mapper_assembly.parsers._message_body_scan import parse_class_fields as _parse_class_fields
from proto_mapper_assembly.parsers._message_body_scan import scan_message_body


def parse_class_fields(class_start: int, code: str) -> list[DumpCSMessageField]:
    return _parse_class_fields(class_start, code)


def parse_message_body(
    stripped_body: str,
    enum_names: frozenset[str] = frozenset(),
) -> tuple[list[DumpCSMessageField], list[DumpCSMessageProperty]]:
    scan_data = scan_message_body(stripped_body, enum_names)
    fields = scan_data.fields
    properties = scan_data.properties
    reconcile_message_body(
        fields=fields,
        properties=properties,
        excluded_boolean_properties=scan_data.excluded_boolean_properties,
        const_int_declarations=scan_data.const_int_declarations,
        field_positions_by_name=scan_data.field_positions_by_name,
    )
    fields.extend(
        build_synthetic_oneof_fields(
            fields=fields,
            properties=properties,
            property_positions_by_name=scan_data.property_positions_by_name,
            field_positions_by_name=scan_data.field_positions_by_name,
            enum_names=enum_names,
        )
    )
    return fields, properties
