from tests.fixtures.proto_mapper.script_builders import (
    empty_enum_signatures as _empty_enum_signatures,
)
from tests.fixtures.proto_mapper.script_builders import (
    game_mapping_entry as _game_mapping_entry,
)
from tests.fixtures.proto_mapper.script_builders import (
    empty_proto_accesses as _empty_proto_accesses,
)
from tests.fixtures.proto_mapper.script_builders import (
    proto_accesses as _proto_accesses,
)
from tests.fixtures.proto_mapper.script_builders import (
    proto_accesses_with_function_infos as _proto_accesses_with_function_infos,
)
from tests.fixtures.proto_mapper.script_builders import (
    script_message as _msg,
)
from tests.fixtures.proto_mapper.script_builders import (
    zero_access_enum_signatures as _enum_signatures,
)
from tests.fixtures.proto_mapper.script_builders import (
    zero_access_field as _field,
)
from tests.fixtures.proto_mapper.signatures import (
    builder_field_access_entry,
    builder_typeinfo_access_entry,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingsDocument
from DBDofusUnity.proto_mapper_assembly.helpers.non_obf_names import build_filtered_message_namespace
from DBDofusUnity.proto_mapper_assembly.scripts.check_zero_access_fields import (
    audit_unknown_fields,
    CoreMethodEvidence,
    collect_zero_access_explanations,
    find_zero_access_fields,
)


class TestFindZeroAccessFields:
    def test_enum_field_with_switch_pattern_is_not_reported(self) -> None:
        msg = _msg(
            "Ns.MyMsg",
            [_field("status", offset=32, category=FieldCategoryEnum.ENUM, enum_value_type="MyEnum")],
        )
        enum_sigs = _enum_signatures({"MyEnum": [32]})
        result = find_zero_access_fields([msg], _empty_proto_accesses(), enum_sigs)
        assert result == []

    def test_enum_field_without_matching_switch_pattern_is_reported(self) -> None:
        msg = _msg(
            "Ns.MyMsg",
            [_field("status", offset=32, category=FieldCategoryEnum.ENUM, enum_value_type="MyEnum")],
        )
        enum_sigs = _enum_signatures({"MyEnum": [40]})
        result = find_zero_access_fields([msg], _empty_proto_accesses(), enum_sigs)
        assert len(result) == 1

    def test_enum_field_with_unknown_enum_type_is_reported(self) -> None:
        msg = _msg(
            "Ns.MyMsg",
            [_field("status", offset=32, category=FieldCategoryEnum.ENUM, enum_value_type="UnknownEnum")],
        )
        result = find_zero_access_fields([msg], _empty_proto_accesses(), _empty_enum_signatures())
        assert len(result) == 1

    def test_non_proto_fields_are_ignored(self) -> None:
        field = _field("_parser", offset=8).model_copy(update={"is_proto_field": False})
        msg = _msg("Ns.MyMsg", [field])
        result = find_zero_access_fields([msg], _empty_proto_accesses(), _empty_enum_signatures())
        assert result == []

    def test_static_fields_are_ignored(self) -> None:
        field = _field("PARSER", offset=0, clr_type="static Parser")
        msg = _msg("Ns.MyMsg", [field])
        result = find_zero_access_fields([msg], _empty_proto_accesses(), _empty_enum_signatures())
        assert result == []

    def test_multiple_messages_multiple_fields(self) -> None:
        msg_a = _msg("Ns.A", [_field("x", 24), _field("y", 32)])
        msg_b = _msg("Ns.B", [_field("z", 24)])
        proto = _proto_accesses([("Ns.A", 24), ("Ns.B", 24)])
        result = find_zero_access_fields([msg_a, msg_b], proto, _empty_enum_signatures())
        assert len(result) == 1
        assert result[0][0] == "Ns.A"
        assert result[0][1].field_name == "y"

    def test_proto_access_on_wrong_cls_does_not_count(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("actor_id", offset=24)])
        proto = _proto_accesses([("Ns.OtherMsg", 24)])
        result = find_zero_access_fields([msg], proto, _empty_enum_signatures())
        assert len(result) == 1


class TestAuditUnknownFields:
    def test_requires_runtime_capture_and_no_evidence_before_dead_candidate(self) -> None:
        non_obf_message = _msg(
            "com.ankama.Msg",
            [
                _field("unknown_ida", 24),
                _field("unknown_runtime", 32),
                _field("unknown_dead", 40),
                _field("known_field", 48),
            ],
        )
        no_capture_message = _msg("com.ankama.NoCapture", [_field("unknown_uncaptured", 24)])
        obf_message = _msg(
            "xyz",
            [
                _field("ida", 24),
                _field("runtime", 32),
                _field("dead", 40),
            ],
        )
        no_capture_obf_message = _msg("abc", [_field("uncaptured", 24)])
        non_obf_messages_by_cls = {
            non_obf_message.composed_name: non_obf_message,
            no_capture_message.composed_name: no_capture_message,
        }
        non_obf_namespace = build_filtered_message_namespace(
            is_obf=False,
            message=non_obf_message,
            messages_by_cls=non_obf_messages_by_cls,
        )
        no_capture_namespace = build_filtered_message_namespace(
            is_obf=False,
            message=no_capture_message,
            messages_by_cls=non_obf_messages_by_cls,
        )
        game_mappings = GameMappingsDocument(
            root={
                non_obf_namespace: _game_mapping_entry(
                    obf_cls=obf_message.composed_name,
                    non_obf_namespace=non_obf_namespace,
                    field_mapping={
                        "ida": "unknown_ida",
                        "runtime": "unknown_runtime",
                        "dead": "unknown_dead",
                    },
                ),
                no_capture_namespace: _game_mapping_entry(
                    obf_cls=no_capture_obf_message.composed_name,
                    non_obf_namespace=no_capture_namespace,
                    field_mapping={"uncaptured": "unknown_uncaptured"},
                ),
            }
        )

        records = audit_unknown_fields(
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            obf_messages_by_cls={
                obf_message.composed_name: obf_message,
                no_capture_obf_message.composed_name: no_capture_obf_message,
            },
            game_mappings=game_mappings,
            accessed_offsets_by_obf_message={obf_message.composed_name: {24}},
            runtime_instances_by_obf_message={
                obf_message.composed_name: ({"ida": 0, "runtime": 5, "dead": 0},),
            },
        )
        records_by_field = {record.non_obf_field: record for record in records}

        assert records_by_field["unknown_ida"].status == "active"
        assert records_by_field["unknown_runtime"].status == "active"
        assert records_by_field["unknown_dead"].status == "dead_candidate"
        assert records_by_field["unknown_uncaptured"].status == "inconclusive"
        assert records_by_field["unknown_uncaptured"].reason == "no_runtime_capture"


class TestCollectZeroAccessExplanations:
    def test_groups_classes_with_existing_offsets_as_partial_field_access(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("seen", 24), _field("missing", 32)])
        explanations = collect_zero_access_explanations(
            [msg],
            _proto_accesses([("Ns.MyMsg", 24)]),
            _empty_enum_signatures(),
        )

        assert len(explanations) == 1
        assert explanations[0].bucket == "partial_field_access"
        assert explanations[0].likely_cause == "partial_missing_offsets"
        assert explanations[0].accessed_offsets == frozenset({24})

    def test_synthetic_oneof_fields_are_reported_with_specific_cause(self) -> None:
        oneof_case_field = _field("contentCase_", 40, category=FieldCategoryEnum.ONEOF).model_copy(
            update={"is_synthetic_oneof_variant": True}
        )
        msg = _msg("Ns.MyMsg", [_field("seen", 24), oneof_case_field])

        explanations = collect_zero_access_explanations(
            [msg],
            _proto_accesses([("Ns.MyMsg", 24)]),
            _empty_enum_signatures(),
        )

        assert len(explanations) == 1
        assert explanations[0].bucket == "partial_field_access"
        assert explanations[0].likely_cause == "synthetic_oneof_case"

    def test_groups_non_stub_seeded_core_methods_separately_from_stubs(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("missing", 24)])
        explanations = collect_zero_access_explanations(
            [msg],
            _empty_proto_accesses(),
            _empty_enum_signatures(),
            {
                "Ns.MyMsg": [
                    CoreMethodEvidence(0x1000, "Core.dll/a", "Boolean stub(MyMsg)", size=2),
                    CoreMethodEvidence(0x2000, "Core.dll/a", "Boolean real(MyMsg)", size=0x80),
                ]
            },
        )

        assert len(explanations) == 1
        assert explanations[0].bucket == "seeded_core_no_fields"
        assert explanations[0].likely_cause == "seeded_proto_param_unused"

    def test_stub_only_seeded_core_method_does_not_create_seeded_bucket(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("missing", 24)])
        explanations = collect_zero_access_explanations(
            [msg],
            _empty_proto_accesses(),
            _empty_enum_signatures(),
            {"Ns.MyMsg": [CoreMethodEvidence(0x1000, "Core.dll/a", "Boolean stub(MyMsg)", size=2)]},
        )

        assert len(explanations) == 1
        assert explanations[0].bucket == "no_core_evidence"
        assert explanations[0].likely_cause == "no_core_evidence"

    def test_groups_typeinfo_only_functions_when_no_field_access_exists(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("missing", 24)])
        proto = _proto_accesses_with_function_infos(
            {
                "Wrapper::.ctor": [
                    builder_typeinfo_access_entry(
                        cls="Ns.MyMsg",
                        instruction_address=0x10,
                        target_address=0x20,
                        index_in_function=0,
                    )
                ]
            }
        )

        explanations = collect_zero_access_explanations([msg], proto, _empty_enum_signatures())

        assert len(explanations) == 1
        assert explanations[0].bucket == "typeinfo_only"
        assert explanations[0].likely_cause == "typeinfo_wrapper_constructor"
        assert explanations[0].typeinfo_only_functions == ["Wrapper::.ctor"]

    def test_typeinfo_dispatch_without_class_field_access_gets_return_only_cause(self) -> None:
        target_msg = _msg("Ns.Target", [_field("missing", 24)])
        other_msg = _msg("Ns.Other", [_field("seen", 24)])
        proto = _proto_accesses_with_function_infos(
            {
                "Dispatcher::Handle(IMessage)": [
                    builder_typeinfo_access_entry(
                        cls="Ns.Target",
                        instruction_address=0x10,
                        target_address=0x20,
                        index_in_function=0,
                    ),
                    builder_typeinfo_access_entry(
                        cls="Ns.Other",
                        instruction_address=0x11,
                        target_address=0x28,
                        index_in_function=0,
                    ),
                    builder_field_access_entry(
                        access_kind="read",
                        cls="Ns.Other",
                        field="seen_",
                        property_name=None,
                        instruction_address=0x30,
                        field_offset=24,
                        index_in_function=0,
                    ),
                ]
            }
        )

        explanations = collect_zero_access_explanations(
            [target_msg, other_msg],
            proto,
            _empty_enum_signatures(),
        )

        assert len(explanations) == 1
        assert explanations[0].cls == "Ns.Target"
        assert explanations[0].bucket == "typeinfo_only"
        assert explanations[0].likely_cause == "typeinfo_dispatch_return_only"
