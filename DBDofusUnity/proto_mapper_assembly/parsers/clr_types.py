from __future__ import annotations

from proto_mapper_assembly.interfaces.field_category import (
    FieldCategoryEnum,
    FieldTypeLeafKind,
    NumericKind,
)
from proto_mapper_assembly.parsers._clr_type_utils import normalize_clr_type

SCALAR_TYPES: frozenset[str] = frozenset(
    {"byte", "sbyte", "short", "ushort", "int", "uint", "long", "ulong", "float", "double"}
)

_ANY_FULL_NAME = "Google.Protobuf.WellKnownTypes.Any"


def categorize_field(clr_type: str, enum_names: frozenset[str]) -> FieldCategoryEnum:
    normalized_type = normalize_clr_type(clr_type)
    if normalized_type == "object":
        return FieldCategoryEnum.ONEOF
    if "RepeatedField" in normalized_type or normalized_type.startswith("["):
        return FieldCategoryEnum.REPEATED
    if "MapField" in normalized_type:
        return FieldCategoryEnum.MAP
    if normalized_type == "string":
        return FieldCategoryEnum.STRING
    if normalized_type == "bool":
        return FieldCategoryEnum.BOOLEAN
    base_type = normalized_type.split("[")[0].split("<")[0].strip()
    if base_type in SCALAR_TYPES:
        return FieldCategoryEnum.NUMBER
    if _resolve_enum_type_name(normalized_type, enum_names) is not None:
        return FieldCategoryEnum.ENUM
    return FieldCategoryEnum.MESSAGE


def resolve_numeric_kind(normalized_type: str | None) -> NumericKind | None:
    """Return the fine-grained scalar numeric kind for a normalized C# type, or None if not scalar."""
    if normalized_type is None:
        return None
    base_type = normalized_type.split("[")[0].split("<")[0].strip()
    if base_type in SCALAR_TYPES:
        return NumericKind(base_type)
    return None


def resolve_non_container_field_kind(
    normalized_type: str | None,
    enum_key_type: str | None,
    enum_value_type: str | None,
) -> FieldTypeLeafKind:
    if normalized_type is None:
        error = "Cannot resolve field kind without normalized_type"
        raise ValueError(error)
    if normalized_type in SCALAR_TYPES:
        return FieldTypeLeafKind.NUMBER
    if normalized_type == "bool":
        return FieldTypeLeafKind.BOOLEAN
    if normalized_type == "string":
        return FieldTypeLeafKind.STRING
    if normalized_type in (enum_key_type, enum_value_type):
        return FieldTypeLeafKind.ENUM
    if is_any_type(normalized_type):
        return FieldTypeLeafKind.ANY
    if normalized_type == "object":
        return FieldTypeLeafKind.ONEOF
    return FieldTypeLeafKind.MESSAGE


def is_any_type(normalized_type: str | None) -> bool:
    if normalized_type is None:
        return False
    if normalized_type == _ANY_FULL_NAME:
        return True
    return normalized_type.rsplit(".", maxsplit=1)[-1] == "Any"


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
