from __future__ import annotations

import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import msg_typed_field
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    NEW_NON_OBF_CLS,
    bootstrap_non_obf_msg,
    existing_non_obf_msg,
    field_signature,
    message_signature,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.pipeline_builders import (
    EXISTING_CLS,
    NON_OBF_CLS,
    bootstrap_repeated_field,
    enum_channel_signature,
    enum_hint_override,
    enum_signature,
    number_dump_field,
    override_only_inputs,
    real_message_signature,
    signature_override_at_offset,
    signature_override_with_indexed_access,
)

from proto_mapper_assembly.controllers.non_obf_bootstrap import (
    inject_synthetic_non_obf_entries_for_override_only_messages,
)
from proto_mapper_assembly.controllers.non_obf_matching_inputs import prepare_non_obf_matching_inputs
from proto_mapper_assembly.controllers.signature_override_application import (
    _apply_field_binding_remapping,
    apply_stored_signature_overrides,
)
from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeShape
from proto_mapper_assembly.interfaces.signature_overrides import FieldOverrideBinding, SignatureOverrideEntry


class TestApplyStoredSignatureOverrides:
    def test_override_replaces_signature_without_mutating_original_mapping(self) -> None:
        field = number_dump_field("field", "Field", 64)
        non_obf_sig = message_signature(
            NON_OBF_CLS,
            declared_field_signatures=[],
            dump_cs_msg=DumpCSMessage(file_descriptor="FD", name="Message", fields=[field]),
        )
        original = {NON_OBF_CLS: non_obf_sig}
        override = signature_override_at_offset(64, field_key=field.field_key)

        result = apply_stored_signature_overrides(original, {NON_OBF_CLS: override}, {})

        overridden = result[NON_OBF_CLS]
        assert result is not original
        assert original[NON_OBF_CLS] is non_obf_sig
        assert overridden.field_signatures == list(override.field_signatures.values())
        assert overridden.message_cls == NON_OBF_CLS
        assert overridden.dump_cs_msg is non_obf_sig.dump_cs_msg

    def test_override_preserves_stored_field_access_indexes(self) -> None:
        field = number_dump_field("field", "Field", 40)
        non_obf_sig = message_signature(
            NON_OBF_CLS,
            declared_field_signatures=[],
            dump_cs_msg=DumpCSMessage(file_descriptor="FD", name="Message", fields=[field]),
        )

        result = apply_stored_signature_overrides(
            {NON_OBF_CLS: non_obf_sig},
            {NON_OBF_CLS: signature_override_with_indexed_access()},
            {},
        )

        indexed_function_access = result[NON_OBF_CLS].function_signatures[0].self_accesses[0]
        indexed_field_access = result[NON_OBF_CLS].field_signatures[0].accesses[0]
        assert indexed_function_access.index_in_function == 7
        assert indexed_field_access.index_in_function == 7

    def test_skips_missing_targets_and_keeps_other_entries(self) -> None:
        other_sig = message_signature("Other", declared_field_signatures=[])
        field = number_dump_field("field", "Field", 32)
        base_sig = message_signature(
            NON_OBF_CLS,
            declared_field_signatures=[],
            dump_cs_msg=DumpCSMessage(file_descriptor="FD", name="Message", fields=[field]),
        )
        override = signature_override_at_offset(field_key=field.field_key)

        assert apply_stored_signature_overrides({}, {NON_OBF_CLS: override}, {}) == {}
        result = apply_stored_signature_overrides(
            {NON_OBF_CLS: base_sig, "Other": other_sig}, {NON_OBF_CLS: override}, {}
        )

        assert result["Other"] is other_sig


class TestInjectSyntheticNonObfEntriesForOverrideOnlyMessages:
    def test_uses_bootstrap_dump_cs_message_for_missing_override_target(self) -> None:
        bootstrap_field = bootstrap_repeated_field()
        inputs = override_only_inputs(bootstrap_field)

        result_msgs, result_sigs = inject_synthetic_non_obf_entries_for_override_only_messages(
            overrides=inputs.overrides,
            bootstrap_messages_by_cls=inputs.bootstrap_messages_by_cls,
            non_obf_messages_by_cls=inputs.non_obf_messages_by_cls,
            non_obf_signatures_by_cls=inputs.non_obf_signatures_by_cls,
        )

        synthetic_msg = result_msgs[NEW_NON_OBF_CLS]
        synthetic_sig = result_sigs[NEW_NON_OBF_CLS]
        assert synthetic_msg.fields[0].property_name == "entities_states"
        assert synthetic_sig.field_signatures == list(
            inputs.overrides[NEW_NON_OBF_CLS].field_signatures.values()
        )
        assert [field.field_key for field in synthetic_sig.dump_cs_msg.fields] == [bootstrap_field.field_key]
        assert synthetic_sig.live_field_keys == frozenset({bootstrap_field.field_key})
        assert [field.property_name for field in synthetic_sig.get_exportable_fields()] == ["entities_states"]

    def test_keeps_existing_non_obf_message_when_present(self) -> None:
        existing_msg = bootstrap_non_obf_msg()
        existing_sig = message_signature(
            NEW_NON_OBF_CLS, declared_field_signatures=[], dump_cs_msg=existing_msg
        )

        result_msgs, result_sigs = inject_synthetic_non_obf_entries_for_override_only_messages(
            overrides={NEW_NON_OBF_CLS: SignatureOverrideEntry(function_signatures=[], field_signatures={})},
            bootstrap_messages_by_cls={NEW_NON_OBF_CLS: bootstrap_non_obf_msg()},
            non_obf_messages_by_cls={EXISTING_CLS: existing_non_obf_msg(), NEW_NON_OBF_CLS: existing_msg},
            non_obf_signatures_by_cls={NEW_NON_OBF_CLS: existing_sig},
        )

        assert result_msgs[NEW_NON_OBF_CLS] is existing_msg
        assert result_sigs[NEW_NON_OBF_CLS] is existing_sig

    def test_raises_when_bootstrap_message_is_missing(self) -> None:
        with pytest.raises(ValueError, match=r"new_dump_cs.json"):
            inject_synthetic_non_obf_entries_for_override_only_messages(
                overrides={
                    NEW_NON_OBF_CLS: SignatureOverrideEntry(function_signatures=[], field_signatures={})
                },
                bootstrap_messages_by_cls={},
                non_obf_messages_by_cls={EXISTING_CLS: existing_non_obf_msg()},
                non_obf_signatures_by_cls={},
            )


class TestPrepareNonObfMatchingInputs:
    def test_applies_bootstrap_messages_and_overrides(self) -> None:
        inputs = override_only_inputs()
        result_msgs, result_sigs = prepare_non_obf_matching_inputs(
            overrides=inputs.overrides,
            bootstrap_messages_by_cls=inputs.bootstrap_messages_by_cls,
            non_obf_messages_by_cls=inputs.non_obf_messages_by_cls,
            non_obf_signatures_by_cls=inputs.non_obf_signatures_by_cls,
            non_obf_enum_signatures_by_name={},
        )

        assert NEW_NON_OBF_CLS in result_msgs
        assert result_sigs[NEW_NON_OBF_CLS].field_signatures == []


class TestStoredFieldBinding:
    def test_remaps_dump_fields_live_keys_and_merges_non_obf_signatures(self) -> None:
        remapped_field = number_dump_field("_actor_id", "actorId", 16)
        preserved_field = number_dump_field("_other", "other", 8)
        non_obf_sig = real_message_signature(
            remapped_field,
            preserved_field,
            live_keys=frozenset({FieldKey(16, "_actor_id")}),
        ).model_copy(
            update={
                "field_signatures": [
                    field_signature(16, None, field_key=remapped_field.field_key),
                    field_signature(8, None, field_key=preserved_field.field_key),
                ]
            }
        )
        obf_sig = field_signature(32, None, field_key=FieldKey(32, "_actor_id"))
        override = SignatureOverrideEntry(
            function_signatures=[],
            field_signatures={"actorId": obf_sig},
            obf_field_binding_by_non_obf_property_name={
                "actorId": FieldOverrideBinding(obf_field_name="_actor_id", obf_memory_offset=32)
            },
        )

        result = apply_stored_signature_overrides({NON_OBF_CLS: non_obf_sig}, {NON_OBF_CLS: override}, {})
        remapped = result[NON_OBF_CLS]

        assert remapped.dump_cs_msg.fields[0].memory_offset == 32
        assert remapped.live_field_keys == frozenset({FieldKey(32, "_actor_id"), FieldKey(8, "_other")})
        assert {field_sig.field_offset for field_sig in remapped.field_signatures} == {8, 32}
        assert obf_sig in remapped.field_signatures

    def test_apply_field_binding_remapping_remaps_matching_fields_only(self) -> None:
        matching_field = number_dump_field("_actor_id", "actorId", 16)
        unmatched_field = number_dump_field("_other", "other", 16)
        no_property_field = number_dump_field("_raw", None, 16)
        msg = DumpCSMessage(
            file_descriptor="FD", name="Msg", fields=[matching_field, unmatched_field, no_property_field]
        )

        result = _apply_field_binding_remapping(
            msg,
            {
                "actorId": FieldOverrideBinding(obf_field_name="_actor_id", obf_memory_offset=32),
                "_raw": FieldOverrideBinding(obf_field_name="_raw", obf_memory_offset=48),
            },
        )

        assert result is not msg
        assert [field.memory_offset for field in result.fields] == [32, 16, 16]
        assert _apply_field_binding_remapping(msg, {}) is msg

    @pytest.mark.parametrize(
        ("override", "expected_error"),
        [
            (
                SignatureOverrideEntry(
                    function_signatures=[],
                    field_signatures={
                        "field": field_signature(32, FieldTypeShape(FieldCategoryEnum.NUMBER, None, None))
                    },
                    obf_field_binding_by_non_obf_property_name={
                        "missing_field": FieldOverrideBinding(obf_field_name="cells_", obf_memory_offset=32)
                    },
                ),
                "unknown field",
            ),
            (
                SignatureOverrideEntry(
                    function_signatures=[],
                    field_signatures={
                        "cells": field_signature(32, FieldTypeShape(FieldCategoryEnum.NUMBER, None, None)),
                        "character_id": field_signature(
                            48, FieldTypeShape(FieldCategoryEnum.REPEATED, None, None)
                        ),
                    },
                    obf_field_binding_by_non_obf_property_name={
                        "cells": FieldOverrideBinding(obf_field_name="cells_", obf_memory_offset=32),
                        "character_id": FieldOverrideBinding(
                            obf_field_name="character_id_", obf_memory_offset=48
                        ),
                    },
                ),
                "Invalid stored field binding",
            ),
        ],
    )
    def test_invalid_field_offset_remapping_raises(
        self, override: SignatureOverrideEntry, expected_error: str
    ) -> None:
        fields = [
            msg_typed_field(
                field_name="cells_",
                property_name="Cells",
                offset=16,
                clr_type="RepeatedField<int>",
                category=FieldCategoryEnum.REPEATED,
            ),
            msg_typed_field(
                field_name="character_id_",
                property_name="CharacterId",
                offset=24,
                clr_type="long",
                category=FieldCategoryEnum.NUMBER,
            ),
        ]
        non_obf_sig = real_message_signature(*fields)

        with pytest.raises(ValueError, match=expected_error):
            apply_stored_signature_overrides({NON_OBF_CLS: non_obf_sig}, {NON_OBF_CLS: override}, {})


class TestEnumSignatureHints:
    def test_accepts_enum_signature_hints_when_field_matches_hint_type(self) -> None:
        non_obf_sig = enum_channel_signature()
        override = enum_hint_override("Channel", {"10": "Global"})

        result = apply_stored_signature_overrides(
            {NON_OBF_CLS: non_obf_sig},
            {NON_OBF_CLS: override},
            non_obf_enum_signatures_by_name={"Channel": enum_signature({"10": "Global"})},
        )

        assert result[NON_OBF_CLS].field_signatures == []

    @pytest.mark.parametrize(
        ("non_obf_sig", "override", "enum_signatures", "expected_error"),
        [
            (
                message_signature(
                    NON_OBF_CLS,
                    declared_field_signatures=[],
                    dump_cs_msg=DumpCSMessage(file_descriptor="FD", name="Msg", fields=[]),
                ),
                enum_hint_override("Channel", {"10": "Global"}),
                {},
                "stored enum signature hint",
            ),
            (
                enum_channel_signature(),
                enum_hint_override("WrongChannel", {"10": "Global"}),
                {},
                "enum type mismatch",
            ),
            (
                enum_channel_signature(),
                enum_hint_override("Channel", {"99": "Missing"}),
                {"Channel": enum_signature({"10": "Global"})},
                "unknown enum member values",
            ),
        ],
    )
    def test_invalid_enum_signature_hints_raise(
        self,
        non_obf_sig: MessageAccessSignature,
        override: SignatureOverrideEntry,
        enum_signatures: dict[str, EnumSignatureEntry],
        expected_error: str,
    ) -> None:
        with pytest.raises(ValueError, match=expected_error):
            apply_stored_signature_overrides(
                {NON_OBF_CLS: non_obf_sig},
                {NON_OBF_CLS: override},
                non_obf_enum_signatures_by_name=enum_signatures,
            )
