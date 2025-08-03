from collections import defaultdict
from unittest.mock import patch

from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.runtime_builders import make_candidate

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.runtime import (
    MessageRuntimeMetadata,
    RemapOutcome,
    RuntimeRemappingContext,
    RuntimeRemappingTraceEvent,
)
from proto_mapper_assembly.runtime.runtime_remapping import _remap_child_message


class TestRemapChildMessage:
    def _minimal_context(self) -> RuntimeRemappingContext:
        return RuntimeRemappingContext(
            candidates_by_non_obf={},
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
            get_obf_metadata=lambda _msg: MessageRuntimeMetadata(
                live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
            ),
            get_non_obf_metadata=lambda _msg: MessageRuntimeMetadata(
                live_runtime_fields_by_name={}, child_message_cls_by_field_key={}
            ),
            resolve_field_mapping_by_pair=lambda _obf, _non_obf: {},
        )

    def test_success_path_returns_remapped_value(self) -> None:
        child_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildObf")
        child_non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildClear")
        child_candidate = make_candidate(child_obf_msg, child_non_obf_msg, {})
        context = self._minimal_context()

        instances_by_type: dict[str, list[dict[str, object]]] = defaultdict(list)
        outcome = _remap_child_message(
            raw_value={},
            child_candidate=child_candidate,
            child_obf_message=child_obf_msg,
            child_non_obf_message=child_non_obf_msg,
            remapping_context=context,
            instances_by_type=instances_by_type,
            trace_handler=None,
            path=(),
        )

        assert outcome.mapping_failure is None
        assert instances_by_type["ChildClear"] == [{}]

    def test_failure_emits_trace_and_propagates(self) -> None:
        child_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildObf")
        child_non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildClear")
        child_candidate = make_candidate(child_obf_msg, child_non_obf_msg, {})
        context = self._minimal_context()

        events: list[RuntimeRemappingTraceEvent] = []
        fail_outcome = RemapOutcome(value={}, mapping_failure="test_failure")
        with patch(
            "proto_mapper_assembly.runtime.runtime_remapping._remap_runtime_instance",
            return_value=fail_outcome,
        ):
            outcome = _remap_child_message(
                raw_value={"key": "val"},
                child_candidate=child_candidate,
                child_obf_message=child_obf_msg,
                child_non_obf_message=child_non_obf_msg,
                remapping_context=context,
                instances_by_type=defaultdict(list),
                trace_handler=events.append,
                path=("root",),
            )

        assert outcome.mapping_failure == "test_failure"
        assert len(events) == 1
        assert events[0].message == "test_failure"
        assert events[0].mapping_failure_origin == "child"
