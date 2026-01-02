from __future__ import annotations

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField, DumpCSMessageProperty
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import normalize_clr_type
from DBDofusUnity.proto_mapper_assembly.parsers.clr_types import categorize_field


def dump_cs_field(
    clr_type: str,
    *,
    offset: int = 0x10,
    field_name: str = "",
    enum_names: frozenset[str] = frozenset(),
) -> DumpCSMessageField:
    normalized_type = normalize_clr_type(clr_type)
    category = categorize_field(clr_type, enum_names)
    enum_value_type = (
        normalized_type if category == FieldCategoryEnum.ENUM and normalized_type in enum_names else None
    )
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=normalized_type,
        category=category,
        memory_offset=offset,
        field_name=field_name,
        enum_value_type=enum_value_type,
    )


_NORMALIZED_TYPE_BY_CATEGORY: dict[FieldCategoryEnum, str] = {
    FieldCategoryEnum.STRING: "String",
    FieldCategoryEnum.NUMBER: "Int32",
    FieldCategoryEnum.BOOLEAN: "Boolean",
    FieldCategoryEnum.ENUM: "Int32",
    FieldCategoryEnum.MESSAGE: "ChildMessage",
    FieldCategoryEnum.REPEATED: "RepeatedField<Int32>",
    FieldCategoryEnum.MAP: "MapField<Int32, Int32>",
}


def dump_field(
    field_name: str,
    property_name: str | None,
    offset: int,
    category: FieldCategoryEnum,
    *,
    proto_decl_order: int | None = None,
) -> DumpCSMessageField:
    normalized_type = _NORMALIZED_TYPE_BY_CATEGORY.get(category, "String")
    return DumpCSMessageField(
        clr_type=normalized_type,
        normalized_type=normalized_type,
        category=category,
        memory_offset=offset,
        field_name=field_name,
        property_name=property_name,
        proto_decl_order=proto_decl_order,
    )


def typed_dump_field(
    *,
    field_name: str,
    property_name: str,
    normalized_type: str,
    category: FieldCategoryEnum,
    offset: int,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=normalized_type,
        normalized_type=normalized_type,
        category=category,
        memory_offset=offset,
        field_name=field_name,
        property_name=property_name,
    )


def number_field(name: str = "value_") -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="int",
        normalized_type="int",
        category=FieldCategoryEnum.NUMBER,
        memory_offset=0x10,
        field_name=name,
        property_name="Value",
    )


def scalar_field(field_name: str, offset: int) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="int",
        normalized_type="int",
        category=FieldCategoryEnum.NUMBER,
        memory_offset=offset,
        field_name=field_name,
    )


def msg_field(field_name: str, offset: int) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="SomeChild",
        normalized_type="SomeChild",
        category=FieldCategoryEnum.MESSAGE,
        memory_offset=offset,
        field_name=field_name,
    )


def repeated_field(field_name: str, offset: int) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="RepeatedField<SomeChild>",
        normalized_type="RepeatedField<SomeChild>",
        category=FieldCategoryEnum.REPEATED,
        memory_offset=offset,
        field_name=field_name,
    )


def map_field(field_name: str, offset: int) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="MapField<int,SomeChild>",
        normalized_type="MapField<int,SomeChild>",
        category=FieldCategoryEnum.MAP,
        memory_offset=offset,
        field_name=field_name,
    )


def make_oneof_field(
    field_name: str,
    offset: int,
    *,
    group_name: str,
    proto_decl_order: int,
    property_name: str | None = None,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="Int32",
        normalized_type="Int32",
        category=FieldCategoryEnum.ONEOF,
        memory_offset=offset,
        field_name=field_name,
        is_synthetic_oneof_variant=True,
        oneof_group_name=group_name,
        proto_decl_order=proto_decl_order,
        property_name=property_name,
    )


def enum_field(
    *,
    field_name: str,
    property_name: str,
    offset: int,
    enum_type: str,
) -> DumpCSMessageField:
    f = dump_field(field_name, property_name, offset, FieldCategoryEnum.ENUM)
    f.clr_type = enum_type
    f.normalized_type = enum_type
    f.enum_key_type = None
    f.enum_value_type = enum_type
    return f


def map_enum_field(
    *,
    field_name: str,
    property_name: str,
    offset: int,
    enum_key_type: str | None = None,
    enum_value_type: str | None = None,
) -> DumpCSMessageField:
    f = dump_field(field_name, property_name, offset, FieldCategoryEnum.MAP)
    key_type = enum_key_type or "int"
    value_type = enum_value_type or "int"
    f.clr_type = f"MapField<{key_type},{value_type}>"
    f.normalized_type = f.clr_type
    f.enum_key_type = enum_key_type
    f.enum_value_type = enum_value_type
    return f


def make_field(
    category: FieldCategoryEnum,
    normalized_type: str,
    *,
    clr_type: str | None = None,
    enum_key_type: str | None = None,
    enum_value_type: str | None = None,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=clr_type or normalized_type,
        normalized_type=normalized_type,
        category=category,
        memory_offset=0x10,
        field_name="field_",
        enum_key_type=enum_key_type,
        enum_value_type=enum_value_type,
    )


def msg_typed_field(
    *,
    field_name: str,
    property_name: str,
    offset: int,
    clr_type: str,
    category: FieldCategoryEnum,
    enum_key_type: str | None = None,
    enum_value_type: str | None = None,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=normalize_clr_type(clr_type),
        category=category,
        memory_offset=offset,
        field_name=field_name,
        property_name=property_name,
        enum_key_type=enum_key_type,
        enum_value_type=enum_value_type,
    )


def dump_cs_int_field(field_name: str, *, is_proto: bool = True) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="int",
        normalized_type="int",
        category=FieldCategoryEnum.NUMBER,
        memory_offset=0x10,
        field_name=field_name,
        is_proto_field=is_proto,
    )


def dump_string_field(field_name: str, *, is_proto: bool = True) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="string",
        normalized_type="string",
        category=FieldCategoryEnum.STRING,
        memory_offset=0x18,
        field_name=field_name,
        is_proto_field=is_proto,
    )


def dump_oneof_field(field_name: str) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type="int",
        normalized_type="int",
        category=FieldCategoryEnum.ONEOF,
        memory_offset=0x20,
        field_name=field_name,
    )


def dump_property(name: str, normalized_type: str = "string") -> DumpCSMessageProperty:
    return DumpCSMessageProperty(
        clr_type=normalized_type,
        normalized_type=normalized_type,
        property_name=name,
    )
