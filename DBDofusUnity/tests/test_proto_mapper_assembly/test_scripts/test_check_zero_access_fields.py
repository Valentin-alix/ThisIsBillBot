from __future__ import annotations

from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    empty_enum_signatures as _empty_enum_signatures,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    empty_proto_accesses as _empty_proto_accesses,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    proto_accesses as _proto_accesses,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    proto_accesses_with_function_infos as _proto_accesses_with_function_infos,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    script_message as _msg,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    zero_access_enum_signatures as _enum_signatures,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import (
    zero_access_field as _field,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.signatures import (
    builder_field_access_entry,
    builder_typeinfo_access_entry,
)

from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.scripts.check_zero_access_fields import (
    CoreMethodEvidence,
    collect_zero_access_explanations,
    find_zero_access_fields,
    format_explain_report,
    format_report,
)


class TestFindZeroAccessFields:
    def test_field_with_proto_access_is_not_reported(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("actor_id", offset=24)])
        proto = _proto_accesses([("Ns.MyMsg", 24)])
        result = find_zero_access_fields([msg], proto, _empty_enum_signatures())
        assert result == []

    def test_field_without_any_access_is_reported(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("actor_id", offset=24)])
        proto = _empty_proto_accesses()
        result = find_zero_access_fields([msg], proto, _empty_enum_signatures())
        assert len(result) == 1
        cls, field = result[0]
        assert cls == "Ns.MyMsg"
        assert field.field_name == "actor_id"

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
        enum_sigs = _enum_signatures({"MyEnum": [40]})  # offset 40 != 32
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


class TestFormatReport:
    def test_empty_report(self) -> None:
        output = format_report([])
        assert "0 zero-access fields" in output

    def test_report_contains_message_and_field_info(self) -> None:
        field = _field("actor_id", offset=24)
        output = format_report([("Ns.MyMsg", field)])
        assert "Ns.MyMsg" in output
        assert "actor_id" in output
        assert "24" in output

    def test_report_summary_counts(self) -> None:
        field_a = _field("x", 24)
        field_b = _field("y", 32)
        output = format_report([("Ns.A", field_a), ("Ns.A", field_b)])
        assert "2 zero-access fields" in output
        assert "1 message" in output


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

    def test_format_explain_report_includes_bucket_and_evidence(self) -> None:
        msg = _msg("Ns.MyMsg", [_field("missing", 24)])
        explanations = collect_zero_access_explanations(
            [msg],
            _empty_proto_accesses(),
            _empty_enum_signatures(),
            {"Ns.MyMsg": [CoreMethodEvidence(0x2000, "Core.dll/a", "Boolean real(MyMsg)", size=0x80)]},
        )

        output = format_explain_report(explanations)

        assert "[likely_cause_summary]" in output
        assert "seeded_proto_param_unused: 1 field(s) across 1 message(s)" in output
        assert "[seeded_core_no_fields]" in output
        assert "likely_cause: seeded_proto_param_unused" in output
        assert "Core.dll/a@0x2000:Boolean real(MyMsg)" in output
