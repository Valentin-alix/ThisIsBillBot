from tests.fixtures.proto_mapper.field_builders import (
    msg_field,
    scalar_field,
)
from tests.fixtures.proto_mapper.runtime_builders import (
    make_candidate,
    make_simple_context,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping import remap_runtime_instances


class TestRemapRuntimeInstancesBasic:
    def test_empty_instances_returns_empty_result(self) -> None:
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {})
        context = make_simple_context(obf_msg, non_obf_msg, {}, {})

        result = remap_runtime_instances(
            normalized_instances=[],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        assert result.instances_by_type == {}

    def testscalar_field_is_remapped(self) -> None:
        obf_field = scalar_field("abc_", 0x10)
        non_obf_field = scalar_field("value_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {"abc_": "value_"})
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"abc_": obf_field},
            non_obf_live_fields={"value_": non_obf_field},
        )

        result = remap_runtime_instances(
            normalized_instances=[{"abc_": 99}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        assert result.instances_by_type["ClearMsg"] == [{"value_": 99}]

    def test_two_instances_accumulated(self) -> None:
        obf_field = scalar_field("f_", 0x10)
        non_obf_field = scalar_field("f_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {})
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"f_": obf_field},
            non_obf_live_fields={"f_": non_obf_field},
        )

        result = remap_runtime_instances(
            normalized_instances=[{"f_": 1}, {"f_": 2}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        assert len(result.instances_by_type["ClearMsg"]) == 2

    def test_unknown_obf_key_is_skipped(self) -> None:
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {})
        context = make_simple_context(obf_msg, non_obf_msg, {}, {})

        result = remap_runtime_instances(
            normalized_instances=[{"ghost_key": 42}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{}]

    def testmessage_field_with_missing_non_obf_field_is_skipped(self) -> None:
        obf_field = msg_field("child_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {"child_": "child_"})
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"child_": obf_field},
            non_obf_live_fields={},  # child_ not in non_obf live fields
        )

        result = remap_runtime_instances(
            normalized_instances=[{"child_": {"f": 1}}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{}]

    def test_number_field_with_missing_non_obf_is_skipped(self) -> None:
        obf_field = scalar_field("val_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")
        candidate = make_candidate(obf_msg, non_obf_msg, {"val_": "missing_"})
        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"val_": obf_field},
            non_obf_live_fields={},  # missing_ not in non_obf live fields
        )

        result = remap_runtime_instances(
            normalized_instances=[{"val_": 7}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{}]
