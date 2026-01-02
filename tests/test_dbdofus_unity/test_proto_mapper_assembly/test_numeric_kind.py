from __future__ import annotations

from tests.fixtures.proto_mapper.field_builders import typed_dump_field

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, NumericKind
from DBDofusUnity.proto_mapper_assembly.scoring.signature_scoring import declared_field_similarity


def _number(normalized_type: str, *, offset: int = 0x10) -> DumpCSMessageField:
    return typed_dump_field(
        field_name=normalized_type,
        property_name="Value",
        normalized_type=normalized_type,
        category=FieldCategoryEnum.NUMBER,
        offset=offset,
    )


class TestNumericKind:
    def test_numeric_kind_resolves_scalar_types(self) -> None:
        assert _number("int").numeric_kind is NumericKind.INT
        assert _number("long").numeric_kind is NumericKind.LONG
        assert _number("uint").numeric_kind is NumericKind.UINT

    def test_numeric_kind_is_none_for_non_scalar(self) -> None:
        string_field = typed_dump_field(
            field_name="s",
            property_name="S",
            normalized_type="string",
            category=FieldCategoryEnum.STRING,
            offset=0x10,
        )
        assert string_field.numeric_kind is None

    def test_declared_shape_token_separates_int_from_long(self) -> None:
        # Same coarse shape (NUMBER) but distinct fine type -> distinct multiset key.
        assert _number("int").declared_shape_token != _number("long").declared_shape_token
        assert _number("int").declared_shape_token == _number("int", offset=0x20).declared_shape_token


class TestDeclaredFieldNumericGrading:
    def test_same_numeric_kind_is_full_similarity(self) -> None:
        assert declared_field_similarity(_number("int"), _number("int")) == 1.0

    def test_mismatched_numeric_kind_is_partial(self) -> None:
        # int32 vs int64: same coarse category, graded down (not 0) so parser noise stays tolerant.
        score = declared_field_similarity(_number("int"), _number("long"))
        assert 0.0 < score < 1.0

    def test_different_category_is_zero(self) -> None:
        string_field = typed_dump_field(
            field_name="s",
            property_name="S",
            normalized_type="string",
            category=FieldCategoryEnum.STRING,
            offset=0x10,
        )
        assert declared_field_similarity(_number("int"), string_field) == 0
