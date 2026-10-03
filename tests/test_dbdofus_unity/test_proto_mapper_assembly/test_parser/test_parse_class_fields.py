from typing import NamedTuple

import pytest

from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers._message_body_scan import scan_message_body


class FieldCase(NamedTuple):
    declaration: str
    category: FieldCategoryEnum
    clr_type: str
    normalized_type: str
    memory_offset: int


class TestScanMessageBody:
    @pytest.mark.parametrize(
        "case",
        [
            FieldCase("private int subareaId_; // 0x18", FieldCategoryEnum.NUMBER, "int", "int", 24),
            FieldCase(
                "private readonly RepeatedField<House> houses_; // 0x28",
                FieldCategoryEnum.REPEATED,
                "RepeatedField<House>",
                "RepeatedField<House>",
                40,
            ),
            FieldCase(
                "private object specificComplementaryInformation_; // 0x60",
                FieldCategoryEnum.ONEOF,
                "object",
                "object",
                96,
            ),
            FieldCase(
                "private readonly MapField<int, House> housesById_; // 0x28",
                FieldCategoryEnum.MAP,
                "MapField<int, House>",
                "MapField<int,House>",
                40,
            ),
            FieldCase(
                "private Direction direction_; // 0x28",
                FieldCategoryEnum.MESSAGE,
                "Direction",
                "Direction",
                40,
            ),
        ],
    )
    def test_parses_supported_instance_fields(self, case: FieldCase) -> None:
        fields = scan_message_body(case.declaration).fields

        assert len(fields) == 1
        assert fields[0].category == case.category
        assert fields[0].clr_type == case.clr_type
        assert fields[0].normalized_type == case.normalized_type
        assert fields[0].memory_offset == case.memory_offset

    def test_infrastructure_field_is_excluded(self) -> None:
        fields = scan_message_body("private UnknownFieldSet _unknownFields; // 0x10").fields
        assert fields == []

    def test_multiple_fields_order_and_count(self) -> None:
        code = (
            "    private int subareaId_; // 0x18\n"
            "    private long mapId_; // 0x20\n"
            "    private readonly RepeatedField<House> houses_; // 0x28\n"
            "    private readonly MapField<int, House> housesById_; // 0x30\n"
            "    private bool active_; // 0x38\n"
            "    private object variant_; // 0x40\n"
        )
        fields = scan_message_body(code).fields
        assert len(fields) == 6
        categories = [f.category for f in fields]
        assert categories == [
            FieldCategoryEnum.NUMBER,
            FieldCategoryEnum.NUMBER,
            FieldCategoryEnum.REPEATED,
            FieldCategoryEnum.MAP,
            FieldCategoryEnum.BOOLEAN,
            FieldCategoryEnum.ONEOF,
        ]

    def test_internal_fields_are_marked_non_proto_without_field_number_markers(self) -> None:
        code = (
            "    private int _hasBits0; // 0x18\n"
            "    private static readonly int ValueDefaultValue; // 0x10\n"
            "    private int value_; // 0x1c\n"
            "    private bool flag_; // 0x20\n"
        )
        fields = scan_message_body(code).fields
        by_name = {field.field_name: field for field in fields}
        assert by_name["_hasBits0"].is_proto_field is False
        assert by_name["value_"].is_proto_field is True
        assert by_name["flag_"].is_proto_field is True
