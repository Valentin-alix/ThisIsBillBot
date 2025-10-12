from __future__ import annotations

import re
from dataclasses import dataclass

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty
from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import (
    extract_map_inner_types,
    extract_repeated_inner_type,
    normalize_clr_type,
)
from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_structure import get_stripped_direct_body
from DBDofusUnity.proto_mapper_assembly.parsers.clr_types import categorize_field

FIELD_PATTERN = re.compile(
    r"(?:public|private|protected)\s+(?:readonly\s+)?(.*?)\s+(\w+)\s*;\s*//\s*0x([0-9a-fA-F]+)",
    re.MULTILINE,
)
_PROPERTY_MODIFIERS_PATTERN = r"(?:(?:override|virtual|abstract|new|sealed)\s+)*"
_PROPERTY_TYPE_PATTERN = r"([^\n{]+?)"
_PROPERTY_NAME_PATTERN = r"([\w:.]+)"
_PROPERTY_ACCESSORS_PATTERN = r"(\{[^}]*\})"
_PROPERTY_COMMENT_PATTERN = r"(?:\s*//\s*([^\n]*))?"
PROPERTY_PATTERN = re.compile(
    rf"public\s+(?!static\s)"
    rf"{_PROPERTY_MODIFIERS_PATTERN}"
    rf"{_PROPERTY_TYPE_PATTERN}\s+"
    rf"{_PROPERTY_NAME_PATTERN}\s*"
    rf"{_PROPERTY_ACCESSORS_PATTERN}"
    rf"{_PROPERTY_COMMENT_PATTERN}",
    re.MULTILINE,
)
_ADDRESS_RANGE_PATTERN = re.compile(r"0x([0-9a-fA-F]+)-0x[0-9a-fA-F]+")
CONST_INT_PATTERN = re.compile(
    r"public\s+const\s+int\s+(\w+)\s*=\s*(\d+)\s*;",
    re.MULTILINE,
)
_PROPERTY_INFRASTRUCTURE_TYPES: frozenset[str] = frozenset({"MessageDescriptor"})
_FIELD_INFRASTRUCTURE_TYPES: frozenset[str] = frozenset({"UnknownFieldSet"})


@dataclass(frozen=True, slots=True)
class _FieldNumberDeclaration:
    property_name: str
    field_number: int
    position: int


@dataclass(frozen=True, slots=True)
class _ConstIntDeclaration:
    constant_name: str
    value: int
    position: int


@dataclass(frozen=True, slots=True)
class _ExcludedBooleanProperty:
    property_name: str
    position: int


@dataclass(frozen=True)
class MessageBodyScanData:
    fields: list[DumpCSMessageField]
    field_positions_by_name: dict[str, int]
    properties: list[DumpCSMessageProperty]
    property_positions_by_name: dict[str, int]
    excluded_boolean_properties: list[_ExcludedBooleanProperty]
    const_int_declarations: list[_ConstIntDeclaration]


def parse_class_fields(class_start: int, code: str) -> list[DumpCSMessageField]:
    stripped_body = get_stripped_direct_body(class_start, code)
    if not stripped_body:
        return []
    fields, _ = _parse_class_fields_and_positions(stripped_body, frozenset())
    return fields


def scan_message_body(
    stripped_body: str,
    enum_names: frozenset[str] = frozenset(),
) -> MessageBodyScanData:
    fields, field_positions_by_name = _parse_class_fields_and_positions(stripped_body, enum_names)
    const_int_declarations = _parse_const_int_declarations_from_stripped_body(stripped_body)
    properties, property_positions_by_name = _parse_class_properties_and_positions_from_stripped_body(
        stripped_body
    )
    return MessageBodyScanData(
        fields=fields,
        field_positions_by_name=field_positions_by_name,
        properties=properties,
        property_positions_by_name=property_positions_by_name,
        excluded_boolean_properties=_parse_excluded_boolean_properties_from_stripped_body(stripped_body),
        const_int_declarations=const_int_declarations,
    )


def _parse_class_fields_and_positions(
    stripped_body: str,
    enum_names: frozenset[str],
) -> tuple[list[DumpCSMessageField], dict[str, int]]:
    fields: list[DumpCSMessageField] = []
    field_positions_by_name: dict[str, int] = {}
    for match in FIELD_PATTERN.finditer(stripped_body):
        field_positions_by_name[match.group(2)] = match.start()
        field = _parse_field_match(match, enum_names)
        if field is not None:
            fields.append(field)
    return fields, field_positions_by_name


def _extract_enum_type_fields(
    normalized_type: str,
    enum_names: frozenset[str],
) -> tuple[str | None, str | None]:
    enum_type_name = _resolve_enum_type_name(normalized_type, enum_names)
    if enum_type_name is not None:
        return None, enum_type_name
    repeated_inner_type = extract_repeated_inner_type(normalized_type)
    if repeated_inner_type is not None:
        repeated_enum_name = _resolve_enum_type_name(repeated_inner_type, enum_names)
        if repeated_enum_name is not None:
            return None, repeated_enum_name
        return None, None
    map_inner_types = extract_map_inner_types(normalized_type)
    if map_inner_types is None:
        return None, None
    return (
        _resolve_enum_type_name(map_inner_types[0], enum_names),
        _resolve_enum_type_name(map_inner_types[1], enum_names),
    )


def _resolve_enum_type_name(
    normalized_type: str,
    enum_names: frozenset[str],
) -> str | None:
    if normalized_type in enum_names:
        return normalized_type
    suffix = normalized_type.rsplit(".", maxsplit=1)[-1]
    if suffix in enum_names:
        return suffix
    return None


def _parse_field_match(
    match: re.Match[str],
    enum_names: frozenset[str],
) -> DumpCSMessageField | None:
    clr_type = match.group(1).strip()
    normalized_type = normalize_clr_type(clr_type)
    field_name = match.group(2)
    if "static" in clr_type:
        return None
    if normalized_type in _FIELD_INFRASTRUCTURE_TYPES:
        return None
    enum_key_type, enum_value_type = _extract_enum_type_fields(normalized_type, enum_names)
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=normalized_type,
        category=categorize_field(clr_type, enum_names),
        memory_offset=int(match.group(3), 16),
        field_name=field_name,
        is_proto_field=not field_name.startswith("_"),
        enum_key_type=enum_key_type,
        enum_value_type=enum_value_type,
    )


def _parse_class_properties_and_positions_from_stripped_body(
    stripped_body: str,
) -> tuple[list[DumpCSMessageProperty], dict[str, int]]:
    properties: list[DumpCSMessageProperty] = []
    property_positions_by_name: dict[str, int] = {}
    for match in PROPERTY_PATTERN.finditer(stripped_body):
        clr_type = match.group(1).strip()
        prop_name = match.group(2)
        accessor_block = match.group(3)
        if not _is_supported_proto_property(clr_type, prop_name, accessor_block):
            continue
        property_positions_by_name[prop_name] = match.start()
        comment = match.group(4) or ""
        getter_address, setter_address = _parse_property_addresses(comment)
        properties.append(
            DumpCSMessageProperty(
                clr_type=clr_type,
                normalized_type=normalize_clr_type(clr_type),
                property_name=prop_name,
                getter_address=getter_address,
                setter_address=setter_address,
            )
        )
    return properties, property_positions_by_name


def _is_supported_proto_property(clr_type: str, prop_name: str, accessor_block: str) -> bool:
    if clr_type in _PROPERTY_INFRASTRUCTURE_TYPES:
        return False
    if clr_type.startswith("MessageParser<"):
        return False
    has_setter = "get; set;" in accessor_block
    if not has_setter and not ("RepeatedField<" in clr_type or "MapField<" in clr_type):
        return False
    return "." not in prop_name and "::" not in prop_name


def _parse_property_addresses(comment: str) -> tuple[int | None, int | None]:
    matches = _ADDRESS_RANGE_PATTERN.findall(comment)
    if not matches:
        return None, None
    getter_address = int(matches[0], 16)
    setter_address = int(matches[1], 16) if len(matches) > 1 else None
    return getter_address, setter_address


def _parse_excluded_boolean_properties_from_stripped_body(
    stripped_body: str,
) -> list[_ExcludedBooleanProperty]:
    excluded_properties: list[_ExcludedBooleanProperty] = []
    for match in PROPERTY_PATTERN.finditer(stripped_body):
        clr_type = match.group(1).strip()
        prop_name = match.group(2)
        accessor_block = match.group(3)
        if clr_type != "bool":
            continue
        if "get; set;" in accessor_block:
            continue
        if "." in prop_name or "::" in prop_name:
            continue
        excluded_properties.append(
            _ExcludedBooleanProperty(
                property_name=prop_name,
                position=match.start(),
            )
        )
    return excluded_properties


def _parse_const_int_declarations_from_stripped_body(
    stripped_body: str,
) -> list[_ConstIntDeclaration]:
    return [
        _ConstIntDeclaration(
            constant_name=match.group(1),
            value=int(match.group(2)),
            position=match.start(),
        )
        for match in CONST_INT_PATTERN.finditer(stripped_body)
    ]
