from __future__ import annotations

from dataclasses import dataclass

from tests.fixtures.proto_mapper.enum_builders import enum_function_ref
from tests.fixtures.proto_mapper.field_builders import dump_field, msg_typed_field
from tests.fixtures.proto_mapper.message_builders import (
    NAMESPACE,
    NEW_NON_OBF_CLS,
    bootstrap_non_obf_msg,
    existing_non_obf_msg,
    field_signature,
    message_signature,
)
from tests.fixtures.proto_mapper.signatures import (
    builder_function_access_signature,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessAtomSignature,
    AccessTraceDocument,
    FieldAccessSignatures,
    FunctionAccessSignature,
    MessageAccessSignature,
    ReturnRole,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import (
    EnumMemberGroup,
    EnumSignatureEntry,
    EnumSwitchPattern,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeShape
from DBDofusUnity.proto_mapper_assembly.interfaces.game_mappings import GameMappingEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchResult
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import (
    EnumSignatureOverrideHint,
    SignatureOverrideEntry,
)

NON_OBF_CLS = "Com.Ankama.RealMessage"
EXISTING_CLS = f"{NAMESPACE}.SomeExistingMsg"


@dataclass(frozen=True)
class OverrideOnlyInputs:
    overrides: dict[str, SignatureOverrideEntry]
    bootstrap_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_messages_by_cls: dict[str, DumpCSMessage]
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature]


def bootstrap_repeated_field() -> DumpCSMessageField:
    return msg_typed_field(
        field_name="entities_states_",
        property_name="entities_states",
        offset=32,
        clr_type="RepeatedField<iyu>",
        category=FieldCategoryEnum.REPEATED,
    )


def signature_override_at_offset(
    offset: int = 32,
    *,
    field_key: FieldKey | None = None,
    field_type_shape: FieldTypeShape | None = None,
) -> SignatureOverrideEntry:
    return SignatureOverrideEntry(
        function_signatures=[],
        field_signatures={
            "field": field_signature(
                offset,
                field_type_shape,
                field_key=field_key or FieldKey(offset, "field"),
            )
        },
    )


def enum_signature(member_value_to_name: dict[str, str]) -> EnumSignatureEntry:
    member_values = [int(member_value) for member_value in member_value_to_name]
    return EnumSignatureEntry(
        member_value_to_name=member_value_to_name,
        switch_patterns=[
            EnumSwitchPattern(
                function_addr=0x1000,
                field_offset=24,
                member_groups=[
                    EnumMemberGroup(
                        member_values=member_values,
                        called_functions=[enum_function_ref(call_target_addr=0x2000)],
                    )
                ],
            )
        ],
    )


def enum_channel_signature() -> MessageAccessSignature:
    message = DumpCSMessage(
        file_descriptor="FD",
        name="Msg",
        fields=[
            msg_typed_field(
                field_name="channel_",
                property_name="Channel",
                offset=16,
                clr_type="Channel",
                category=FieldCategoryEnum.ENUM,
                enum_value_type="Channel",
            )
        ],
    )
    return MessageAccessSignature(
        message_cls=NON_OBF_CLS,
        file_descriptor=message.file_descriptor,
        dump_cs_msg=message,
        function_signatures=[],
        field_signatures=[],
    )


def enum_hint_override(
    non_obf_enum_type: str, member_value_to_name: dict[str, str]
) -> SignatureOverrideEntry:
    return SignatureOverrideEntry(
        function_signatures=[],
        field_signatures={},
        enum_signature_hints_by_non_obf_prop_name={
            "channel": {
                "value": EnumSignatureOverrideHint(
                    non_obf_enum_type=non_obf_enum_type,
                    signature=enum_signature(member_value_to_name),
                )
            }
        },
    )


def builder_stored_access_function_signature(*, offset: int, access_index: int) -> FunctionAccessSignature:
    number_shape = FieldTypeShape(FieldCategoryEnum.NUMBER, None, None)
    return builder_function_access_signature(
        return_role=ReturnRole.VOID,
        takes_message_parameter=False,
        size=64,
        self_accesses=[
            AccessAtomSignature(
                entry_type="field",
                access_kind="write",
                field_type_shape=number_shape,
                field_offset=offset,
                index_in_function=access_index,
            )
        ],
        foreign_access_summary=[],
    )


def signature_override_with_indexed_access(
    *, offset: int = 40, access_index: int = 7
) -> SignatureOverrideEntry:
    number_shape = FieldTypeShape(FieldCategoryEnum.NUMBER, None, None)
    indexed_field_access = AccessAtomSignature(
        entry_type="field",
        access_kind="write",
        field_type_shape=number_shape,
        field_offset=offset,
        index_in_function=access_index,
    )
    return SignatureOverrideEntry(
        function_signatures=[
            builder_stored_access_function_signature(offset=offset, access_index=access_index)
        ],
        field_signatures={
            "field": FieldAccessSignatures(
                field_key=FieldKey(offset, "field"),
                field_type_shape=number_shape,
                accesses=[indexed_field_access],
            )
        },
    )


def number_dump_field(name: str, property_name: str | None, offset: int) -> DumpCSMessageField:
    return dump_field(name, property_name, offset, FieldCategoryEnum.NUMBER)


def real_message_with_fields(fields: list[DumpCSMessageField]) -> DumpCSMessage:
    return DumpCSMessage(file_descriptor="FD", name="Msg", fields=fields)


def real_message_signature(
    *fields: DumpCSMessageField, live_keys: frozenset[FieldKey] = frozenset()
) -> MessageAccessSignature:
    return message_signature(
        NON_OBF_CLS,
        declared_field_signatures=[],
        dump_cs_msg=real_message_with_fields(list(fields)),
        live_field_keys=live_keys,
    )


def override_only_inputs(field: DumpCSMessageField | None = None) -> OverrideOnlyInputs:
    overrides = (
        {
            NEW_NON_OBF_CLS: signature_override_at_offset(
                field.memory_offset, field_key=field.field_key, field_type_shape=field.field_type_shape
            )
        }
        if field is not None
        else {NEW_NON_OBF_CLS: SignatureOverrideEntry(function_signatures=[], field_signatures={})}
    )
    return OverrideOnlyInputs(
        overrides=overrides,
        bootstrap_messages_by_cls={
            NEW_NON_OBF_CLS: bootstrap_non_obf_msg(fields=[] if field is None else [field])
        },
        non_obf_messages_by_cls={EXISTING_CLS: existing_non_obf_msg()},
        non_obf_signatures_by_cls={},
    )


def simple_match_result(
    *,
    non_obf_cls: str = "ClearA",
    obf_cls: str = "obf_a",
    score: float = 0.9,
    field_mapping: dict[str, str] | None = None,
) -> MatchResult:
    return MatchResult(
        non_obf_signature=message_signature(non_obf_cls, declared_field_signatures=[]),
        obf_signature=message_signature(obf_cls, declared_field_signatures=[]),
        score=score,
        group_similarity_score=score,
        assembly_similarity_score=score,
        structure_similarity_score=score,
        field_mapping=field_mapping or {},
        field_mapping_infos={},
        runtime_confidence=None,
        match_margin=0.0,
        runner_up_obf=None,
        is_low_confidence=False,
        field_mapping_rejected_infos={},
        field_mapping_unmapped_non_obf_fields={},
        evidence_coverage=None,
        is_runtime_observed=False,
    )


def builder_matching_inputs(
    *,
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    obf_signatures_by_cls: dict[str, MessageAccessSignature],
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature],
) -> MatchingInputs:
    return MatchingInputs(
        obf_messages_by_cls=obf_messages_by_cls,
        non_obf_messages_by_cls=non_obf_messages_by_cls,
        obf_signatures_by_cls=obf_signatures_by_cls,
        non_obf_signatures_by_cls=non_obf_signatures_by_cls,
        signature_overrides_by_non_obf_cls={},
        obf_enum_signatures_by_name={},
        non_obf_enum_signatures_by_name={},
        obf_access_trace=AccessTraceDocument(functions_by_address={}),
        non_obf_access_trace=AccessTraceDocument(functions_by_address={}),
    )


def detailed_game_mapping_entry(obf_cls: str, field_mapping: dict[str, str]) -> GameMappingEntry:
    return GameMappingEntry(
        full_obf_msg_namespace=f"{obf_cls}_full",
        obf_msg_namespace=obf_cls,
        full_non_obf_msg_namespace=".Clear",
        field_mapping=field_mapping,
        field_mapping_infos={},
        field_mapping_rejected_infos={},
        field_mapping_unmapped_non_obf_fields={},
        similarity_score=0.9,
        group_similarity_score=0.8,
        assembly_similarity_score=0.7,
        structure_similarity_score=0.6,
        runtime_confidence=None,
        match_margin=0.0,
        runner_up_obf=None,
        is_low_confidence=False,
        evidence_coverage=None,
    )
