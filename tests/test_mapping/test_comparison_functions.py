import unittest

from proto_schema_parser import FieldCardinality

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

    def test_compare_p_field_basic_types(self):
        """Test field comparison with basic protobuf types."""
        test_msg = PMessage(
            name="TestMessage",
            elements=[
                PField(type_name="int32", name="field1", number=1),
                PField(type_name="string", name="field2", number=2),
            ],
            namespace=".test.TestMessage",
        )

        field_int32_1 = PField(type_name="int32", name="field_a", number=1)
        field_int32_2 = PField(type_name="int32", name="field_b", number=2)
        field_string = PField(type_name="string", name="field_c", number=3)
        field_bool = PField(type_name="bool", name="field_d", number=4)

        sim_same_type, _, _ = (
            self.p_mapper.hungarian_solver_service.field_comparison_service.compare_p_field(
                self.p_mapper.get_comparison_message,
                test_msg,
                field_int32_1,
                test_msg,
                field_int32_2,
                set(),
            )
        )
        assert 0 <= sim_same_type <= 1
        assert sim_same_type > 0.5, "Same type fields should have high similarity"

        sim_diff_type, _, _ = (
            self.p_mapper.hungarian_solver_service.field_comparison_service.compare_p_field(
                self.p_mapper.get_comparison_message,
                test_msg,
                field_int32_1,
                test_msg,
                field_string,
                set(),
            )
        )
        assert 0 <= sim_diff_type <= 1
        assert sim_diff_type < sim_same_type, (
            "Different type fields should have lower similarity"
        )

        sim_very_diff, _, _ = (
            self.p_mapper.hungarian_solver_service.field_comparison_service.compare_p_field(
                self.p_mapper.get_comparison_message,
                test_msg,
                field_int32_1,
                test_msg,
                field_bool,
                set(),
            )
        )
        assert 0 <= sim_very_diff <= 1

    def test_compare_p_field_repeated_vs_singular(self):
        """Test that repeated vs singular fields have different similarities."""
        test_msg = PMessage(
            name="TestMessage", elements=[], namespace=".test.TestMessage"
        )

        field_singular = PField(
            type_name="int32", name="field1", number=1, cardinality=None
        )
        field_repeated = PField(
            type_name="int32",
            name="field2",
            number=2,
            cardinality=FieldCardinality.REPEATED,
        )

        sim_repeated_vs_singular, _, _ = (
            self.p_mapper.hungarian_solver_service.field_comparison_service.compare_p_field(
                self.p_mapper.get_comparison_message,
                test_msg,
                field_singular,
                test_msg,
                field_repeated,
                set(),
            )
        )
        sim_singular_vs_singular, _, _ = (
            self.p_mapper.hungarian_solver_service.field_comparison_service.compare_p_field(
                self.p_mapper.get_comparison_message,
                test_msg,
                field_singular,
                test_msg,
                field_singular,
                set(),
            )
        )

        assert 0 <= sim_repeated_vs_singular <= 1
        assert 0 <= sim_singular_vs_singular <= 1
        assert sim_singular_vs_singular >= sim_repeated_vs_singular, (
            "Same cardinality should have higher similarity"
        )

    def test_verified_message_mapping_simple(self):
        """Test a few verified messages to ensure mapping works."""
        test_cases = [
            ("hbo", "SpellsEvent"),
            ("hyp", "InventoryContentEvent"),
        ]

        for obf_name, clear_name in test_cases:
            obf_namespace = None
            for namespace in self.p_mapper.obf_struct_by_namespace:
                if namespace.split(".")[-1] == obf_name:
                    obf_namespace = namespace
                    break

            clear_namespace = None
            for namespace in self.p_mapper.clear_struct_by_namespace:
                if namespace.split(".")[-1] == clear_name:
                    clear_namespace = namespace
                    break

            if obf_namespace and clear_namespace:
                obf_msg = self.p_mapper.obf_struct_by_namespace[obf_namespace]
                clear_msg = self.p_mapper.clear_struct_by_namespace[clear_namespace]

                if isinstance(obf_msg, PMessage) and isinstance(clear_msg, PMessage):
                    mapping_info = self.p_mapper.get_comparison_message(
                        clear_msg, obf_msg, set()
                    )

                    assert 0 <= mapping_info.similarity <= 1, (
                        f"Similarity for {clear_name} should be between 0 and 1"
                    )
                    assert mapping_info.similarity > 0, (
                        f"Verified message {clear_name} should have positive similarity"
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

    def test_reliability_calculation_consistency(self):
        """Test that reliability calculation is consistent."""
        clear_msg = PMessage(
            name="TestMsg",
            elements=[
                PField(type_name="int32", name="field1", number=1),
            ],
            namespace=".test.TestMsg",
        )

        obf_msg = PMessage(
            name="xyz",
            elements=[
                PField(type_name="int32", name="abc", number=1),
            ],
            namespace="xyz",
        )

        reliability_by_indexes = self.p_mapper.hungarian_solver_service.reliability_calculator.get_flat_reliability_by_indexes(
            clear_msg, obf_msg, set()
        )

        assert reliability_by_indexes is not None, "Should return reliability data"

        import numpy as np

        if isinstance(reliability_by_indexes, np.ndarray):
            assert reliability_by_indexes.size > 0, "Should have reliability data"
            assert np.all(reliability_by_indexes >= 0), (
                "All reliabilities should be non-negative"
            )
        elif isinstance(reliability_by_indexes, (list, tuple)):
            assert len(reliability_by_indexes) > 0, "Should have reliability data"
            for row in reliability_by_indexes:
                if isinstance(row, (list, tuple)):
                    for reliability in row:
                        assert reliability >= 0, "Reliability should be non-negative"
                else:
                    assert row >= 0, "Reliability should be non-negative"


if __name__ == "__main__":
    unittest.main()
