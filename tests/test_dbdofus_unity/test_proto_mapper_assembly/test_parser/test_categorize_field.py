from typing import Any

import pytest

from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers.clr_types import categorize_field

_CATEGORIZE_PARAMS: list[tuple[str, frozenset[Any], FieldCategoryEnum]] = [
    ("int", frozenset(), FieldCategoryEnum.NUMBER),
    ("bool", frozenset(), FieldCategoryEnum.BOOLEAN),
    ("string", frozenset(), FieldCategoryEnum.STRING),
    ("object", frozenset(), FieldCategoryEnum.ONEOF),
    ("RepeatedField<House>", frozenset(), FieldCategoryEnum.REPEATED),
    ("MapField<int, House>", frozenset(), FieldCategoryEnum.MAP),
    ("Direction", frozenset({"Direction"}), FieldCategoryEnum.ENUM),
    ("UnknownFieldSet", frozenset(), FieldCategoryEnum.MESSAGE),
]


class TestCategorizeField:
    @pytest.mark.parametrize(
        ("clr_type", "enum_names", "expected"),
        _CATEGORIZE_PARAMS,
    )
    def test_categorizes_scalar_container_enum_and_message_shapes(
        self, clr_type: str, enum_names: frozenset[str], expected: FieldCategoryEnum
    ) -> None:
        assert categorize_field(clr_type, enum_names) == expected

    @pytest.mark.parametrize(
        "clr_type",
        [
            "static readonly MessageParser<Foo>",
            "static readonly FieldCodec<House>",
        ],
    )
    def test_recognizes_static_readonly_message_helpers_as_messages(self, clr_type: str) -> None:
        assert categorize_field(clr_type, frozenset()) == FieldCategoryEnum.MESSAGE
