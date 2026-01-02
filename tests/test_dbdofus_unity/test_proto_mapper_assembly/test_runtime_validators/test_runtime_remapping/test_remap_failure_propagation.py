from unittest.mock import patch

from tests.fixtures.proto_mapper.field_builders import (
    map_field,
    repeated_field,
)
from tests.fixtures.proto_mapper.runtime_builders import (
    make_candidate,
    make_simple_context,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import MessageRuntimeMetadata, RemapOutcome
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping import remap_runtime_instances


class TestRemapFailurePropagation:
    def test_repeated_field_failure_stops_iteration(self) -> None:
        parent_obf_field = repeated_field("items_", 0x10)
        parent_non_obf_field = repeated_field("items_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")

        # Set up a resolved child so the REPEATED branch is entered
        child_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildObf")
        child_non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildClear")
        child_candidate = make_candidate(child_obf_msg, child_non_obf_msg, {})
        child_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
        )
        child_non_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
        )
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"items_": parent_obf_field},
            non_obf_live_fields={"items_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "items_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "items_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata={"ChildObf": child_obf_meta},
            extra_non_obf_metadata={"ChildClear": child_non_obf_meta},
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"items_": "items_"})

        fail_outcome = RemapOutcome(value={}, mapping_failure="child_fail")
        with patch(
            "DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping._remap_child_message",
            return_value=fail_outcome,
        ):
            result = remap_runtime_instances(
                normalized_instances=[{"items_": [{"val_": 1}]}, {"items_": [{"val_": 2}]}],
                candidate=candidate,
                obf_message=obf_msg,
                non_obf_message=non_obf_msg,
                remapping_context=context,
            )

        assert result.mapping_failure == "child_fail"

    def testmap_field_failure_stops_iteration(self) -> None:
        parent_obf_field = map_field("map_", 0x10)
        parent_non_obf_field = map_field("map_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")

        child_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildObf")
        child_non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildClear")
        child_candidate = make_candidate(child_obf_msg, child_non_obf_msg, {})
        child_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
        )
        child_non_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
        )
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"map_": parent_obf_field},
            non_obf_live_fields={"map_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "map_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "map_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata={"ChildObf": child_obf_meta},
            extra_non_obf_metadata={"ChildClear": child_non_obf_meta},
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"map_": "map_"})

        fail_outcome = RemapOutcome(value={}, mapping_failure="map_child_fail")
        with patch(
            "DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping._remap_child_message",
            return_value=fail_outcome,
        ):
            result = remap_runtime_instances(
                normalized_instances=[{"map_": {"k": {"val_": 1}}}],
                candidate=candidate,
                obf_message=obf_msg,
                non_obf_message=non_obf_msg,
                remapping_context=context,
            )

        assert result.mapping_failure == "map_child_fail"
