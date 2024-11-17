import unittest
from unittest.mock import MagicMock

from D3Mapping.d3_mapping.mapping.global_proto_mapper import GlobalProtoMapper
from D3Mapping.d3_mapping.models.mapping_metrics import MappingMetrics
from D3Mapping.d3_mapping.models.p_enum import PEnum
from D3Mapping.d3_mapping.models.p_message import PField, PMessage


class TestIncrementalMapping(unittest.TestCase):
    def setUp(self):
        self.clear_msg1 = PMessage(
            name="Message1",
            namespace=".test.Message1",
            elements=[
                PField(type_name="int32", name="field1", number=1),
                PField(type_name="string", name="field2", number=2),
            ],
        )

        self.clear_msg2 = PMessage(
            name="Message2",
            namespace=".test.Message2",
            elements=[
                PField(type_name="int32", name="fieldA", number=1),
                PField(type_name="bool", name="fieldB", number=2),
            ],
        )

        self.obf_msg1 = PMessage(
            name="abc",
            namespace="abc",
            elements=[
                PField(type_name="int32", name="xyz", number=1),
                PField(type_name="string", name="def", number=2),
            ],
        )

        self.obf_msg2 = PMessage(
            name="ghi",
            namespace="ghi",
            elements=[
                PField(type_name="int32", name="jkl", number=1),
                PField(type_name="bool", name="mno", number=2),
            ],
        )

        self.clear_struct_by_namespace: dict[str, PMessage | PEnum] = {
            ".test.Message1": self.clear_msg1,
            ".test.Message2": self.clear_msg2,
        }

        self.obf_struct_by_namespace: dict[str, PMessage | PEnum] = {
            "abc": self.obf_msg1,
            "ghi": self.obf_msg2,
        }

    def test_get_validator_priority_caches_results(self):
        mapper = GlobalProtoMapper(
            obf_root_namespaces=["abc"],
            clear_struct_by_namespace=self.clear_struct_by_namespace,
            obf_struct_by_namespace=self.obf_struct_by_namespace,
            verified_msg_by_obf={},
            metrics=MappingMetrics(),
            pulp_solver_service=MagicMock(),
            hungarian_solver_service=MagicMock(),
            mapping_enforcement_service=MagicMock(),
            added_mapping_by_obf_namespaces={},
            msg_mapping_info_by_clear_namespace={},
        )

        mapper._build_indices()

        verified_msg = {"abc": "Message1"}

        priority1 = mapper._get_validator_priority("abc", verified_msg)
        priority2 = mapper._get_validator_priority("abc", verified_msg)

        assert priority1 == priority2
        assert (
            mapper._validator_priority_cache is not None
            and "abc" in mapper._validator_priority_cache
        )


if __name__ == "__main__":
    unittest.main()
