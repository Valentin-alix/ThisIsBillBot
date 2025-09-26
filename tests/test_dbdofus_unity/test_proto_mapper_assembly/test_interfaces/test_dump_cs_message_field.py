import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import (
    dump_field,
    make_oneof_field,
)

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessageField
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum


class TestDumpCSMessageField:
    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            (dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER), True),
            (
                dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER).model_copy(
                    update={"is_proto_field": False}
                ),
                False,
            ),
            (
                dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER).model_copy(
                    update={"is_synthetic_oneof_variant": True}
                ),
                False,
            ),
            (
                dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER).model_copy(
                    update={"clr_type": "static int"}
                ),
                False,
            ),
            (
                dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER).model_copy(
                    update={"clr_type": "UnknownFieldSet"}
                ),
                False,
            ),
        ],
    )
    def test_is_instance_backed_proto_field_filters_non_exportable_cases(
        self,
        field: DumpCSMessageField,
        expected: bool,
    ) -> None:
        assert field.is_instance_backed_proto_field is expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            (
                make_oneof_field(
                    "Request",
                    0x18,
                    group_name="choice",
                    proto_decl_order=1,
                    property_name="Request",
                ),
                True,
            ),
            (
                make_oneof_field(
                    "Request",
                    0x18,
                    group_name="choice",
                    proto_decl_order=1,
                    property_name="Request",
                ).model_copy(update={"is_proto_field": False}),
                False,
            ),
            (
                make_oneof_field(
                    "Request",
                    0x18,
                    group_name="choice",
                    proto_decl_order=1,
                    property_name="Request",
                ).model_copy(update={"clr_type": "static Request"}),
                False,
            ),
            (
                make_oneof_field(
                    "Request",
                    0x18,
                    group_name="choice",
                    proto_decl_order=1,
                    property_name="Request",
                ).model_copy(update={"clr_type": "UnknownFieldSet"}),
                False,
            ),
        ],
    )
    def test_is_property_traceable_proto_field_keeps_synthetic_oneof_variants(
        self,
        field: DumpCSMessageField,
        expected: bool,
    ) -> None:
        assert field.is_property_traceable_proto_field is expected

    @pytest.mark.parametrize(
        ("field", "expected"),
        [
            (dump_field("value_", "MapId", 0x10, FieldCategoryEnum.NUMBER), "map_id"),
            (dump_field("types_", "Types_", 0x20, FieldCategoryEnum.REPEATED), "types"),
            (dump_field("value_", None, 0x10, FieldCategoryEnum.NUMBER), "value"),
        ],
    )
    def test_clean_field_name_uses_property_or_trimmed_field_name(
        self,
        field: DumpCSMessageField,
        expected: str,
    ) -> None:
        assert field.clean_field_name == expected
