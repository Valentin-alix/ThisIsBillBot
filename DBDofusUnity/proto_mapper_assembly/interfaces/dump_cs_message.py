from __future__ import annotations

from collections import Counter
from functools import cached_property
from typing import NamedTuple, override

from utils.string_utils import camel_to_snake
from pydantic import BaseModel, Field

from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import (
    FieldCategoryEnum,
    FieldTypeShape,
    NumericKind,
)
from DBDofusUnity.proto_mapper_assembly.parsers._clr_type_utils import extract_map_inner_types, extract_repeated_inner_type
from DBDofusUnity.proto_mapper_assembly.parsers.clr_types import resolve_non_container_field_kind, resolve_numeric_kind

_INFRASTRUCTURE_TYPES: frozenset[str] = frozenset({"UnknownFieldSet"})


class FieldKey(NamedTuple):
    memory_offset: int
    field_name: str


class EnumFieldTypes(NamedTuple):
    key: str | None
    value: str | None


def normalize_proto_field_name(field_name: str) -> str:
    """Return the canonical proto-style field name for a C# dump field/property, E.G : (Truc_ => truc)."""
    return camel_to_snake(field_name).removesuffix("_")


class DumpCSMessageProperty(BaseModel):
    clr_type: str
    normalized_type: str
    property_name: str
    getter_address: int | None = None
    setter_address: int | None = None


class DumpCSMessageField(BaseModel):
    clr_type: str
    normalized_type: str
    category: FieldCategoryEnum
    memory_offset: int
    field_name: str
    is_proto_field: bool = True
    property_name: str | None = None
    proto_decl_order: int | None = None
    oneof_group_name: str | None = None
    is_synthetic_oneof_variant: bool = False
    enum_key_type: str | None = None
    enum_value_type: str | None = None

    def has_enum_type(self, type_name: str) -> bool:
        return type_name in self.enum_field_types

    @cached_property
    def enum_field_types(self) -> EnumFieldTypes:
        return EnumFieldTypes(key=self.enum_key_type, value=self.enum_value_type)

    @cached_property
    def clean_field_name(self) -> str:
        if self.property_name is not None:
            return normalize_proto_field_name(self.property_name)
        return self.field_name.rstrip("_")

    @cached_property
    def is_instance_backed_proto_field(self) -> bool:
        if not self.is_proto_field:
            return False
        if self.is_synthetic_oneof_variant:
            return False
        if self.clr_type.startswith("static"):
            return False
        return self.clr_type not in _INFRASTRUCTURE_TYPES

    @cached_property
    def is_property_traceable_proto_field(self) -> bool:
        if not self.is_proto_field:
            return False
        if self.property_name is None:
            return False
        if self.clr_type.startswith("static"):
            return False
        return self.clr_type not in _INFRASTRUCTURE_TYPES

    @cached_property
    def is_declared_proto_shape_field(self) -> bool:
        if not self.is_proto_field:
            return False
        if self.clr_type.startswith("static"):
            return False
        if self.clr_type in _INFRASTRUCTURE_TYPES:
            return False
        return self.category != FieldCategoryEnum.ONEOF or self.is_synthetic_oneof_variant

    @cached_property
    def field_type_shape(self) -> FieldTypeShape:
        if self.category == FieldCategoryEnum.MESSAGE:
            return FieldTypeShape(
                category=FieldCategoryEnum.MESSAGE,
                inner_kind=resolve_non_container_field_kind(
                    self.normalized_type, self.enum_key_type, self.enum_value_type
                ),
                outer_kind=None,
            )

        if self.category == FieldCategoryEnum.REPEATED:
            repeated_inner_type = extract_repeated_inner_type(self.normalized_type)
            repeated_inner_kind = resolve_non_container_field_kind(
                repeated_inner_type, self.enum_key_type, self.enum_value_type
            )
            return FieldTypeShape(
                category=FieldCategoryEnum.REPEATED, inner_kind=repeated_inner_kind, outer_kind=None
            )

        if self.category == FieldCategoryEnum.MAP:
            map_inner_types = extract_map_inner_types(self.normalized_type)
            if map_inner_types is None:
                error = f"Cannot parse map inner types for {self.field_name}: {self.normalized_type}"
                raise ValueError(error)
            key_kind = resolve_non_container_field_kind(
                map_inner_types[0], self.enum_key_type, self.enum_value_type
            )
            value_kind = resolve_non_container_field_kind(
                map_inner_types[1], self.enum_key_type, self.enum_value_type
            )
            return FieldTypeShape(category=FieldCategoryEnum.MAP, inner_kind=key_kind, outer_kind=value_kind)

        return FieldTypeShape(category=self.category, inner_kind=None, outer_kind=None)

    @cached_property
    def numeric_kind(self) -> NumericKind | None:
        if self.category != FieldCategoryEnum.NUMBER:
            return None
        return resolve_numeric_kind(self.normalized_type)

    @cached_property
    def declared_shape_token(self) -> str:
        """Stable multiset key for structure scoring; refines the coarse shape with ``numeric_kind``."""
        if self.numeric_kind is None:
            return str(self.field_type_shape)
        return f"{self.field_type_shape}|{self.numeric_kind.value}"

    @property
    def field_key(self) -> FieldKey:
        return FieldKey(self.memory_offset, self.field_name)


class DumpCSMessage(BaseModel):
    file_descriptor: str
    name: str
    fields: list[DumpCSMessageField] = Field(default_factory=list[DumpCSMessageField])
    properties: list[DumpCSMessageProperty] = Field(default_factory=list[DumpCSMessageProperty])
    namespace: str | None = None
    parent_name: str | None = None
    base_class_name: str | None = None

    @override
    def __hash__(self) -> int:
        return self.composed_name.__hash__()

    @property
    def is_root_msg(self) -> bool:
        return not self.parent_name

    @cached_property
    def oneof_group_sizes(self) -> tuple[int, ...]:
        """Sorted member counts of each declared oneof group, an obfuscation-stable fingerprint."""
        group_sizes: Counter[str] = Counter()
        for field in self.fields:
            if not field.is_declared_proto_shape_field or field.oneof_group_name is None:
                continue
            group_sizes[field.oneof_group_name] += 1
        return tuple(sorted(group_sizes.values()))

    @cached_property
    def composed_name(self) -> str:
        if self.parent_name is not None:
            return f"{self.parent_name}.{self.name}"
        if self.namespace is not None:
            return f"{self.namespace}.{self.name}"
        return self.name
