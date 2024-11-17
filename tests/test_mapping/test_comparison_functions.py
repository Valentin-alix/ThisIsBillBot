import unittest

from D3Mapping.d3_mapping.consts import OBFUSCATED_PROTO_GAME, PROTO_GAME_PATH
from D3Mapping.d3_mapping.factories.p_mapper_factory import PMapperFactory
from D3Mapping.d3_mapping.mapping.services.enum_comparison_service import compare_p_enum
from D3Mapping.d3_mapping.models.p_enum import PEnum, PEnumElement
from D3Mapping.d3_mapping.models.p_message import PField, PMessage
from D3Mapping.d3_mapping.verified_mapping import (
    GAME_VERIFIED_MAPPING,
)


class TestComparisonFunctions(unittest.TestCase):
    """Test individual comparison functions in the mapping engine."""

    def setUp(self):
        self.p_mapper = PMapperFactory.create_p_mapper(
            PROTO_GAME_PATH,
            OBFUSCATED_PROTO_GAME,
            GAME_VERIFIED_MAPPING,
        )

    def test_compare_p_enum(self):
        """Test enum comparison returns valid similarity score."""

        enum1 = PEnum(
            name="TestEnum1",
            namespace=".test.TestEnum1",
            elements=[
                PEnumElement("A", 1),
                PEnumElement("B", 2),
                PEnumElement("C", 3),
            ],
        )
        enum2 = PEnum(
            name="TestEnum2",
            namespace=".test.TestEnum2",
            elements=[
                PEnumElement("X", 1),
                PEnumElement("Y", 2),
                PEnumElement("Z", 3),
            ],
        )
        enum3 = PEnum(
            name="TestEnum3",
            namespace=".test.TestEnum3",
            elements=[PEnumElement("P", 1), PEnumElement("Q", 2)],
        )

        sim_same_length = compare_p_enum(enum1, enum2)
        assert 0 <= sim_same_length <= 1, "Similarity should be between 0 and 1"
        assert sim_same_length > 0.5, "Same length enums should have high similarity"

        sim_diff_length = compare_p_enum(enum1, enum3)
        assert 0 <= sim_diff_length <= 1, "Similarity should be between 0 and 1"
        assert sim_diff_length < sim_same_length, (
            "Different length enums should have lower similarity"
        )

    def test_field_mapping_returns_valid_structure(self):
        """Test that field mapping returns expected structure."""
        clear_msg_namespace = (
            ".com.ankama.dofus.server.game.protocol.inventory.ObjectItem"
        )
        obf_msg_namespace = "bpcb"

        if (
            clear_msg_namespace in self.p_mapper.clear_struct_by_namespace
            and obf_msg_namespace in self.p_mapper.obf_struct_by_namespace
        ):
            clear_msg = self.p_mapper.clear_struct_by_namespace[clear_msg_namespace]
            obf_msg = self.p_mapper.obf_struct_by_namespace[obf_msg_namespace]

            if isinstance(clear_msg, PMessage) and isinstance(obf_msg, PMessage):
                mapping_info = self.p_mapper.get_comparison_message(
                    clear_msg, obf_msg, set()
                )

                assert isinstance(mapping_info.field_mapping, dict)

                for obf_field_name, mapping in mapping_info.field_mapping.items():
                    assert isinstance(obf_field_name, str)
                    if mapping is not None:
                        sim, clear_field_name, sub_mapping, _ = mapping
                        assert 0 <= sim <= 1, (
                            "Field similarity should be between 0 and 1"
                        )
                        assert isinstance(clear_field_name, str)

    def test_flat_field_mapping_symmetry(self):
        """Test that flat field mapping is consistent."""
        clear_msg = PMessage(
            name="SimpleMessage",
            elements=[
                PField(type_name="int32", name="id", number=1),
                PField(type_name="string", name="name", number=2),
                PField(type_name="bool", name="active", number=3),
            ],
            namespace=".test.SimpleMessage",
        )

        obf_msg = PMessage(
            name="abc",
            elements=[
                PField(type_name="int32", name="xyz", number=1),
                PField(type_name="string", name="def", number=2),
                PField(type_name="bool", name="ghi", number=3),
            ],
            namespace="abc",
        )

        from D3Mapping.d3_mapping.mapping.services.proto_organization_service import (
            ProtoOrganization,
        )

        clear_elems = ProtoOrganization.get_flat_elements(clear_msg)
        obf_elems = ProtoOrganization.get_flat_elements(obf_msg)

        total_sim, total_reliability, field_mapping, audit = (
            self.p_mapper.hungarian_solver_service.get_flat_best_field_mapping_combination(
                self.p_mapper.get_comparison_message,
                clear_msg,
                obf_msg,
                clear_elems,
                obf_elems,
                set(),
            )
        )

        assert total_sim >= 0, "Total similarity should be non-negative"
        assert total_reliability >= 0, "Total reliability should be non-negative"
        assert len(field_mapping) == 3, "Should map all 3 obfuscated fields"

        for obf_field_name in field_mapping:
            assert obf_field_name in [
                "xyz",
                "def",
                "ghi",
            ], f"Unexpected field name: {obf_field_name}"


if __name__ == "__main__":
    unittest.main()
