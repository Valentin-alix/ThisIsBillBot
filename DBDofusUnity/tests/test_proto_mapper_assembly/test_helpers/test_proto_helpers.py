import pytest
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.helper_builders import (
    proto_field,
    resolve_message_case,
    type_index,
)

from proto_mapper_assembly.helpers.proto_helpers import (
    extract_child_type_name,
    resolve_message_cls,
)
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeLeafKind


class TestProtoHelpers:
    @pytest.mark.parametrize(
        ("category", "normalized_type", "expected_shape"),
        [
            (FieldCategoryEnum.NUMBER, "Int32", (FieldCategoryEnum.NUMBER, None, None)),
            (FieldCategoryEnum.BOOLEAN, "Boolean", (FieldCategoryEnum.BOOLEAN, None, None)),
            (
                FieldCategoryEnum.MESSAGE,
                "SomeMessage",
                (FieldCategoryEnum.MESSAGE, FieldTypeLeafKind.MESSAGE, None),
            ),
            (
                FieldCategoryEnum.MAP,
                "MapField<int,bool>",
                (FieldCategoryEnum.MAP, FieldTypeLeafKind.NUMBER, FieldTypeLeafKind.BOOLEAN),
            ),
        ],
    )
    def test_build_field_type_shape(
        self,
        category: FieldCategoryEnum,
        normalized_type: str,
        expected_shape: tuple[FieldCategoryEnum, FieldTypeLeafKind | None, FieldTypeLeafKind | None],
    ) -> None:
        shape = proto_field(category, normalized_type).field_type_shape

        assert shape == expected_shape

    def test_field_type_shape_raises_for_invalid_map_shape(self) -> None:
        with pytest.raises(ValueError, match="Cannot parse map inner types"):
            _ = proto_field(FieldCategoryEnum.MAP, "NotAMapField").field_type_shape

    @pytest.mark.parametrize(
        ("category", "normalized_type", "expected_child_type"),
        [
            (FieldCategoryEnum.MAP, "MapField<int,int>", None),
            (FieldCategoryEnum.MAP, "UnknownContainerType", None),
            (FieldCategoryEnum.MAP, "MapField<int,SomeMessage>", "SomeMessage"),
            (FieldCategoryEnum.NUMBER, "Int32", None),
        ],
    )
    def test_extract_child_type_name(
        self,
        category: FieldCategoryEnum,
        normalized_type: str,
        expected_child_type: str | None,
    ) -> None:
        result = extract_child_type_name(proto_field(category, normalized_type))

        assert result == expected_child_type

    @pytest.mark.parametrize(
        "case_name",
        [
            "direct",
            "namespace",
            "parent",
            "single_short_name",
            "ambiguous_namespace_match",
            "ambiguous_no_match",
            "missing",
        ],
    )
    def test_resolve_message_cls(self, case_name: str) -> None:
        case = resolve_message_case(case_name)

        result = resolve_message_cls(
            type_name=case.type_name,
            parent_message=case.parent_message,
            messages_by_cls=case.messages_by_cls,
            type_index=type_index(case.messages_by_cls),
        )

        assert result == case.expected
