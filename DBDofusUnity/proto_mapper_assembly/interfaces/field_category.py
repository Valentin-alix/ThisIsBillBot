from collections.abc import Sequence
from enum import StrEnum, auto
from typing import Annotated, Any, NamedTuple, cast

from pydantic import BeforeValidator, PlainSerializer

_CATEGORY_INDEX = 0
_INNER_KIND_INDEX = 1
_OUTER_KIND_INDEX = 2


class FieldCategoryEnum(StrEnum):
    NUMBER = auto()
    ENUM = auto()
    BOOLEAN = auto()
    STRING = auto()
    MESSAGE = auto()
    REPEATED = auto()
    MAP = auto()
    ONEOF = auto()


class FieldTypeLeafKind(StrEnum):
    NUMBER = auto()
    BOOLEAN = auto()
    STRING = auto()
    ENUM = auto()
    ANY = auto()
    MESSAGE = auto()
    ONEOF = auto()


class NumericKind(StrEnum):
    BYTE = auto()
    SBYTE = auto()
    SHORT = auto()
    USHORT = auto()
    INT = auto()
    UINT = auto()
    LONG = auto()
    ULONG = auto()
    FLOAT = auto()
    DOUBLE = auto()


class FieldTypeShape(NamedTuple):
    category: FieldCategoryEnum
    inner_kind: FieldTypeLeafKind | None
    outer_kind: FieldTypeLeafKind | None


def _coerce_leaf_kind(value: object) -> FieldTypeLeafKind | None:
    return None if value is None else FieldTypeLeafKind(value)


def parse_field_type_shape(value: object) -> object:
    """Accept a FieldTypeShape, a bare category string, or a (legacy or trimmed) array."""
    if isinstance(value, FieldTypeShape):
        return value
    if isinstance(value, str):
        return FieldTypeShape(category=FieldCategoryEnum(value), inner_kind=None, outer_kind=None)
    if not isinstance(value, Sequence):
        return value
    parts: list[Any] = list(cast("Sequence[Any]", value))
    return FieldTypeShape(
        category=FieldCategoryEnum(parts[_CATEGORY_INDEX]),
        inner_kind=_coerce_leaf_kind(parts[_INNER_KIND_INDEX]) if len(parts) > _INNER_KIND_INDEX else None,
        outer_kind=_coerce_leaf_kind(parts[_OUTER_KIND_INDEX]) if len(parts) > _OUTER_KIND_INDEX else None,
    )


def serialize_field_type_shape(shape: FieldTypeShape) -> str | list[str | None]:
    """Compact form: a bare primitive collapses to its category string; null tails are dropped."""
    parts: list[str | None] = [
        shape.category.value,
        shape.inner_kind.value if shape.inner_kind is not None else None,
        shape.outer_kind.value if shape.outer_kind is not None else None,
    ]
    while len(parts) > 1 and parts[-1] is None:
        parts.pop()
    if len(parts) == 1:
        return shape.category.value
    return parts


# Pydantic-facing shape that reads both the legacy `[cat, inner, outer]` array and the compact
# form, and writes the compact form to JSON. Use this on persisted model fields; keep the bare
# `FieldTypeShape` for in-memory keys.
CompactFieldTypeShape = Annotated[
    FieldTypeShape,
    BeforeValidator(parse_field_type_shape),
    PlainSerializer(serialize_field_type_shape, when_used="json"),
]
