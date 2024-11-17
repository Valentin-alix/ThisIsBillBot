import unittest
from typing import cast
from unittest.mock import MagicMock

from D3Mapping.d3_mapping.mapping.global_proto_mapper import GlobalProtoMapper
from D3Mapping.d3_mapping.models.mapping_info import MappingInfo, OutputMappingInfo
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

    def test_map_new_messages_basic(self):
        mapper = GlobalProtoMapper(
            obf_root_namespaces=["abc", "ghi"],
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

        cast(
            MagicMock, mapper.mapping_enforcement_service.enforce_message_comparison
        ).side_effect = (
            lambda clear_msg, obf_msg, comparison_fn, treated: comparison_fn(
                clear_msg, obf_msg, treated
            )
        )
        cast(
            MagicMock,
            mapper.hungarian_solver_service.get_flat_best_field_mapping_combination,
        ).return_value = (
            1.0,
            1.0,
            {"xyz": (1.0, "field1", None), "def": (1.0, "field2", None)},
        )

        new_messages = {"abc": "Message1"}

        new_mappings = mapper.map_new_messages(new_messages)

        assert len(new_mappings) == 1
        assert ".test.Message1" in new_mappings
        assert new_mappings[".test.Message1"].obf_msg_namespace == "abc"

    def test_map_new_messages_reuses_existing_mappings(self):
        mapper = GlobalProtoMapper(
            obf_root_namespaces=["abc", "ghi"],
            clear_struct_by_namespace=self.clear_struct_by_namespace,
            obf_struct_by_namespace=self.obf_struct_by_namespace,
            verified_msg_by_obf={},
            metrics=MappingMetrics(),
            pulp_solver_service=MagicMock(),
            hungarian_solver_service=MagicMock(),
            mapping_enforcement_service=MagicMock(),
            added_mapping_by_obf_namespaces={},
            msg_mapping_info_by_clear_namespace={
                ".test.Message1": OutputMappingInfo(
                    obf_msg_namespace="abc",
                    field_mapping={"xyz": "field1", "def": "field2"},
                )
            },
        )

        cast(
            MagicMock, mapper.mapping_enforcement_service.enforce_message_comparison
        ).side_effect = (
            lambda clear_msg, obf_msg, comparison_fn, treated: comparison_fn(
                clear_msg, obf_msg, treated
            )
        )
        cast(
            MagicMock,
            mapper.hungarian_solver_service.get_flat_best_field_mapping_combination,
        ).return_value = (
            1.0,
            1.0,
            {"jkl": (1.0, "fieldA", None), "mno": (1.0, "fieldB", None)},
        )

        new_messages = {"ghi": "Message2"}

        initial_count = len(mapper.msg_mapping_info_by_clear_namespace)

        new_mappings = mapper.map_new_messages(new_messages)

        assert len(new_mappings) == 1
        assert ".test.Message2" in new_mappings

        total_count = len(mapper.msg_mapping_info_by_clear_namespace)
        assert total_count == initial_count + 1

        assert ".test.Message1" in mapper.msg_mapping_info_by_clear_namespace
        assert ".test.Message2" in mapper.msg_mapping_info_by_clear_namespace

    def test_map_new_messages_skips_nonexistent_clear_messages(self):
        mapper = GlobalProtoMapper(
            obf_root_namespaces=["abc", "ghi"],
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

        cast(
            MagicMock, mapper.mapping_enforcement_service.enforce_message_comparison
        ).side_effect = (
            lambda clear_msg, obf_msg, comparison_fn, treated: comparison_fn(
                clear_msg, obf_msg, treated
            )
        )

        new_messages = {
            "abc": "NonExistentMessage",
            "ghi": "Message2",
        }

        cast(
            MagicMock,
            mapper.hungarian_solver_service.get_flat_best_field_mapping_combination,
        ).return_value = (
            1.0,
            1.0,
            {"jkl": (1.0, "fieldA", None), "mno": (1.0, "fieldB", None)},
        )

        new_mappings = mapper.map_new_messages(new_messages)

        assert len(new_mappings) == 1
        assert ".test.Message2" in new_mappings
        assert ".test.NonExistentMessage" not in new_mappings

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

    def test_map_new_messages_reuses_sub_message_mappings(self):
        sub_clear_msg = PMessage(
            name="SubMessage",
            namespace=".test.SubMessage",
            elements=[
                PField(type_name="int32", name="subField", number=1),
            ],
        )

        sub_obf_msg = PMessage(
            name="sub_obf",
            namespace="sub_obf",
            elements=[
                PField(type_name="int32", name="subObfField", number=1),
            ],
        )

        parent_clear_msg = PMessage(
            name="ParentMessage",
            namespace=".test.ParentMessage",
            elements=[
                PField(
                    type_name=".test.SubMessage",
                    name="nestedField",
                    number=1,
                ),
            ],
        )

        parent_obf_msg = PMessage(
            name="parent_obf",
            namespace="parent_obf",
            elements=[
                PField(type_name="sub_obf", name="nestedObfField", number=1),
            ],
        )

        clear_structs: dict[str, PMessage | PEnum] = {
            ".test.SubMessage": sub_clear_msg,
            ".test.ParentMessage": parent_clear_msg,
        }

        obf_structs: dict[str, PMessage | PEnum] = {
            "sub_obf": sub_obf_msg,
            "parent_obf": parent_obf_msg,
        }

        mapper = GlobalProtoMapper(
            obf_root_namespaces=["sub_obf", "parent_obf"],
            clear_struct_by_namespace=clear_structs,
            obf_struct_by_namespace=obf_structs,
            verified_msg_by_obf={},
            metrics=MappingMetrics(),
            pulp_solver_service=MagicMock(),
            hungarian_solver_service=MagicMock(),
            mapping_enforcement_service=MagicMock(),
            added_mapping_by_obf_namespaces={},
            msg_mapping_info_by_clear_namespace={
                ".test.SubMessage": OutputMappingInfo(
                    obf_msg_namespace="sub_obf",
                    field_mapping={"subObfField": "subField"},
                )
            },
        )

        cast(
            MagicMock, mapper.mapping_enforcement_service.enforce_message_comparison
        ).side_effect = (
            lambda clear_msg, obf_msg, comparison_fn, treated: comparison_fn(
                clear_msg, obf_msg, treated
            )
        )

        cast(
            MagicMock,
            mapper.hungarian_solver_service.get_flat_best_field_mapping_combination,
        ).return_value = (
            1.0,
            1.0,
            {
                "nestedObfField": (
                    1.0,
                    "nestedField",
                    MappingInfo(
                        clear_msg_namespace=".test.SubMessage",
                        similarity=1.0,
                        field_mapping={"subObfField": (1.0, "subField", None, None)},
                    ),
                )
            },
        )

        new_messages = {"parent_obf": "ParentMessage"}

        new_mappings = mapper.map_new_messages(new_messages)

        assert len(new_mappings) == 1
        assert ".test.ParentMessage" in new_mappings

        assert ".test.SubMessage" in mapper.msg_mapping_info_by_clear_namespace
        assert ".test.ParentMessage" in mapper.msg_mapping_info_by_clear_namespace


if __name__ == "__main__":
    unittest.main()
