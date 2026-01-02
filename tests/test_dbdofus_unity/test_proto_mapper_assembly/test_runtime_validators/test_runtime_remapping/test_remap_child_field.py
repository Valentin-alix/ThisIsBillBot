from tests.fixtures.proto_mapper.field_builders import (
    map_field,
    msg_field,
    repeated_field,
    scalar_field,
)
from tests.fixtures.proto_mapper.runtime_builders import (
    make_candidate,
    make_simple_context,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.runtime import MessageRuntimeMetadata, RuntimeValidationCandidate
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_remapping import remap_runtime_instances


class TestRemapChildField:
    """Tests for MESSAGE/REPEATED/MAP field remapping via child candidates."""

    def _build_child_setup(
        self,
    ) -> tuple[
        DumpCSMessage,
        DumpCSMessage,
        DumpCSMessage,
        DumpCSMessage,
        RuntimeValidationCandidate,
        dict[str, MessageRuntimeMetadata],
        dict[str, MessageRuntimeMetadata],
    ]:
        child_obf_field = scalar_field("val_", 0x10)
        child_non_obf_field = scalar_field("value_", 0x10)
        child_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildObf")
        child_non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ChildClear")
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")

        child_candidate = make_candidate(child_obf_msg, child_non_obf_msg, {"val_": "value_"})
        child_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={"val_": child_obf_field},
            child_message_cls_by_field_key={},
        )
        child_non_obf_meta = MessageRuntimeMetadata(
            live_runtime_fields_by_name={"value_": child_non_obf_field},
            child_message_cls_by_field_key={},
        )
        return (
            obf_msg,
            non_obf_msg,
            child_obf_msg,
            child_non_obf_msg,
            child_candidate,
            {"ChildObf": child_obf_meta},
            {"ChildClear": child_non_obf_meta},
        )

    def test_message_field_recursively_remaps_child(self) -> None:
        (
            obf_msg,
            non_obf_msg,
            _child_obf_msg,
            _child_non_obf_msg,
            child_candidate,
            extra_obf_meta,
            extra_non_obf_meta,
        ) = self._build_child_setup()

        parent_obf_field = msg_field("child_", 0x10)
        parent_non_obf_field = msg_field("child_", 0x10)

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"child_": parent_obf_field},
            non_obf_live_fields={"child_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata=extra_obf_meta,
            extra_non_obf_metadata=extra_non_obf_meta,
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"child_": "child_"})

        result = remap_runtime_instances(
            normalized_instances=[{"child_": {"val_": 42}}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        assert result.instances_by_type["ClearMsg"] == [{"child_": {"value_": 42}}]
        assert result.instances_by_type["ChildClear"] == [{"value_": 42}]

    def test_message_field_with_non_dict_value_returns_raw(self) -> None:
        # MESSAGE field but raw_value is not a dict â†’ raw_value returned as-is
        parent_obf_field = msg_field("child_", 0x10)
        parent_non_obf_field = msg_field("child_", 0x10)
        (
            obf_msg,
            non_obf_msg,
            _child_obf_msg,
            _child_non_obf_msg,
            child_candidate,
            extra_obf_meta,
            extra_non_obf_meta,
        ) = self._build_child_setup()

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"child_": parent_obf_field},
            non_obf_live_fields={"child_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata=extra_obf_meta,
            extra_non_obf_metadata=extra_non_obf_meta,
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"child_": "child_"})

        result = remap_runtime_instances(
            normalized_instances=[{"child_": "not_a_dict"}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{"child_": "not_a_dict"}]

    def test_repeated_field_remaps_dict_items_passes_through_scalars(self) -> None:
        parent_obf_field = repeated_field("items_", 0x10)
        parent_non_obf_field = repeated_field("items_", 0x10)
        (
            obf_msg,
            non_obf_msg,
            _child_obf_msg,
            _child_non_obf_msg,
            child_candidate,
            extra_obf_meta,
            extra_non_obf_meta,
        ) = self._build_child_setup()

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"items_": parent_obf_field},
            non_obf_live_fields={"items_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "items_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "items_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata=extra_obf_meta,
            extra_non_obf_metadata=extra_non_obf_meta,
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"items_": "items_"})

        result = remap_runtime_instances(
            normalized_instances=[{"items_": [{"val_": 1}, "scalar_item", {"val_": 2}]}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        items = result.instances_by_type["ClearMsg"][0]["items_"]
        assert isinstance(items, list)
        assert items[0] == {"value_": 1}
        assert items[1] == "scalar_item"
        assert items[2] == {"value_": 2}

    def test_map_field_remaps_dict_values_passes_through_scalars(self) -> None:
        parent_obf_field = map_field("map_", 0x10)
        parent_non_obf_field = map_field("map_", 0x10)
        (
            obf_msg,
            non_obf_msg,
            _child_obf_msg,
            _child_non_obf_msg,
            child_candidate,
            extra_obf_meta,
            extra_non_obf_meta,
        ) = self._build_child_setup()

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"map_": parent_obf_field},
            non_obf_live_fields={"map_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "map_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "map_"): "ChildClear"},
            candidates_by_non_obf={"ChildClear": {"ChildObf": child_candidate}},
            extra_obf_metadata=extra_obf_meta,
            extra_non_obf_metadata=extra_non_obf_meta,
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"map_": "map_"})

        result = remap_runtime_instances(
            normalized_instances=[{"map_": {"k1": {"val_": 10}, "k2": 99}}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.mapping_failure is None
        mapped = result.instances_by_type["ClearMsg"][0]["map_"]
        assert isinstance(mapped, dict)
        assert mapped["k1"] == {"value_": 10}
        assert mapped["k2"] == 99

    def test_unresolved_child_obf_cls_returns_raw_value(self) -> None:
        # child_message_cls_by_field_key returns None â†’ unresolved â†’ raw value
        parent_obf_field = msg_field("child_", 0x10)
        parent_non_obf_field = msg_field("child_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"child_": parent_obf_field},
            non_obf_live_fields={"child_": parent_non_obf_field},
            obf_child_cls_by_key={},  # field_key NOT present â†’ obf_child_cls = None â†’ unresolved
            non_obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildClear"},
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"child_": "child_"})

        result = remap_runtime_instances(
            normalized_instances=[{"child_": {"raw": "data"}}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{"child_": {"raw": "data"}}]

    def test_unresolved_child_no_candidate_returns_raw_value(self) -> None:
        # child_cls known but not in candidates_by_non_obf â†’ unresolved
        parent_obf_field = msg_field("child_", 0x10)
        parent_non_obf_field = msg_field("child_", 0x10)
        obf_msg = DumpCSMessage(file_descriptor="FD", name="ObfMsg")
        non_obf_msg = DumpCSMessage(file_descriptor="FD", name="ClearMsg")

        context = make_simple_context(
            obf_msg,
            non_obf_msg,
            obf_live_fields={"child_": parent_obf_field},
            non_obf_live_fields={"child_": parent_non_obf_field},
            obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildObf"},
            non_obf_child_cls_by_key={FieldKey(0x10, "child_"): "ChildClear"},
            candidates_by_non_obf={},  # "ChildClear" NOT in candidates_by_non_obf
        )
        candidate = make_candidate(obf_msg, non_obf_msg, {"child_": "child_"})

        result = remap_runtime_instances(
            normalized_instances=[{"child_": {"raw": "data"}}],
            candidate=candidate,
            obf_message=obf_msg,
            non_obf_message=non_obf_msg,
            remapping_context=context,
        )

        assert result.instances_by_type["ClearMsg"] == [{"child_": {"raw": "data"}}]
