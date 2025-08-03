from __future__ import annotations

from collections.abc import Sequence

import numpy as np
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_message_lookup,
    build_verified_mapping,
    field_signature,
    message_signature,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.shapes import MESSAGE_SHAPE, NUMBER_SHAPE
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.signatures import declared_field_signature

from proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
    MessageAccessSignature,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum, FieldTypeShape
from proto_mapper_assembly.interfaces.field_mapping import FieldMappingContext
from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.matching import (
    MatchingWorkspace,
    MatchResult,
    PreparedScoreData,
)
from proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.matching.pair_selection import (
    SelectedSignaturePair,
    select_signature_pairs,
)
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.signature_overrides import SignatureOverrideEntry
from proto_mapper_assembly.matching.orchestrator import match_messages, select_grouped_matches
from proto_mapper_assembly.matching.score_preparation import build_prepared_scores
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


def simple_signature(message_cls: str) -> MessageAccessSignature:
    return message_signature(message_cls, declared_field_signatures=[])


def number_signature(message_cls: str) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
    )


def counted_number_signature(message_cls: str, count: int) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)] * count,
    )


def shaped_signature(message_cls: str, *shapes: FieldTypeShape) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[declared_field_signature(shape) for shape in shapes],
    )


def number_root_signature(message_cls: str, *, name: str | None = None) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
        dump_cs_msg=DumpCSMessage(file_descriptor="GameReflection", name=name or message_cls),
    )


def number_nested_signature(message_cls: str, *, parent_name: str, name: str) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
        dump_cs_msg=DumpCSMessage(
            file_descriptor="GameReflection",
            name=name,
            parent_name=parent_name,
        ),
    )


def grouped_number_signature(message_cls: str, file_descriptor: str) -> MessageAccessSignature:
    return number_signature(message_cls).model_copy(update={"file_descriptor": file_descriptor})


def root_signature(message_cls: str) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[],
        dump_cs_msg=DumpCSMessage(file_descriptor="FD", name=message_cls),
    )


def nested_signature(message_cls: str, *, parent_name: str, name: str) -> MessageAccessSignature:
    return message_signature(
        message_cls,
        declared_field_signatures=[],
        dump_cs_msg=DumpCSMessage(file_descriptor="FD", name=name, parent_name=parent_name),
    )


def simple_workspace(
    *,
    obf_classes: tuple[str, ...] = ("obf_alpha", "obf_beta"),
    non_obf_classes: tuple[str, ...] = ("ClearAlpha", "ClearBeta"),
) -> MatchingWorkspace:
    return build_matching_workspace(
        obf_signatures=[simple_signature(message_cls) for message_cls in obf_classes],
        non_obf_signatures=[simple_signature(message_cls) for message_cls in non_obf_classes],
        obf_messages_by_cls={},
        non_obf_messages_by_cls={},
    )


def prepared_scores_from_matrix(scores_matrix: np.ndarray) -> PreparedScoreData:
    zeros = np.zeros_like(scores_matrix)
    return PreparedScoreData(
        final_scores_matrix=scores_matrix,
        structure_scores_matrix=zeros,
        assembly_scores_matrix=zeros,
        runtime_confidence_by_pair={},
        file_descriptor_similarity_by_pair={},
    )


def fake_field_mapping_context(
    runtime_data_store: RuntimeDataStore,
    *,
    score_by_pair: dict[MatchPairKey, float] | None = None,
) -> FieldMappingContext:
    return FieldMappingContext(
        runtime_data_store=runtime_data_store,
        score_by_pair=score_by_pair or {},
        signature_overrides_by_non_obf_cls={},
        obf_enum_signatures_by_name={},
        non_obf_enum_signatures_by_name={},
        obf_access_trace=EMPTY_ACCESS_TRACE,
        non_obf_access_trace=EMPTY_ACCESS_TRACE,
    )


def message_field(
    *,
    clr_type: str,
    field_name: str,
    property_name: str,
    offset: int = 0x18,
) -> DumpCSMessageField:
    return DumpCSMessageField(
        clr_type=clr_type,
        normalized_type=clr_type,
        category=FieldCategoryEnum.MESSAGE,
        memory_offset=offset,
        field_name=field_name,
        property_name=property_name,
    )


def message_with_child_field(
    *,
    name: str,
    child_type: str,
    field_name: str,
    property_name: str,
) -> DumpCSMessage:
    return DumpCSMessage(
        file_descriptor="GameReflection",
        name=name,
        fields=[
            message_field(
                clr_type=child_type,
                field_name=field_name,
                property_name=property_name,
            )
        ],
    )


def child_message_mapping_signatures() -> tuple[
    MessageAccessSignature,
    MessageAccessSignature,
    dict[str, DumpCSMessage],
    dict[str, DumpCSMessage],
]:
    non_obf_child = DumpCSMessage(file_descriptor="GameReflection", name="StatedElement")
    obf_child = DumpCSMessage(file_descriptor="GameReflection", name="abc")
    non_obf_message = message_with_child_field(
        name="MapComplementaryInformationEvent",
        child_type="StatedElement",
        field_name="stated_element_",
        property_name="StatedElement",
    )
    obf_message = message_with_child_field(
        name="isu",
        child_type="abc",
        field_name="a",
        property_name="Faaa",
    )
    non_obf_signature = message_signature(
        "MapComplementaryInformationEvent",
        declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
        field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
        live_field_keys=frozenset({FieldKey(0x18, "stated_element_")}),
        dump_cs_msg=non_obf_message,
    )
    obf_signature = message_signature(
        "isu",
        declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
        field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
        live_field_keys=frozenset({FieldKey(0x18, "a")}),
        dump_cs_msg=obf_message,
    )
    return (
        non_obf_signature,
        obf_signature,
        build_message_lookup([non_obf_message, non_obf_child]),
        build_message_lookup([obf_message, obf_child]),
    )


def prospective_child_constraint_workspace() -> MatchingWorkspace:
    obf_parent_message = DumpCSMessage(
        file_descriptor="GameReflection",
        name="obf_parent",
        fields=[message_field(clr_type="obf_child", field_name="child_", property_name="Child")],
    )
    obf_child_message = DumpCSMessage(file_descriptor="GameReflection", name="obf_child")
    clear_parent_message = DumpCSMessage(
        file_descriptor="GameReflection",
        name="ClearParent",
        fields=[message_field(clr_type="ClearChild", field_name="child_", property_name="Child")],
    )
    clear_child_message = DumpCSMessage(file_descriptor="GameReflection", name="ClearChild")
    other_clear_message = DumpCSMessage(file_descriptor="GameReflection", name="OtherClear")

    return build_matching_workspace(
        obf_signatures=[
            message_signature(
                "obf_parent",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                dump_cs_msg=obf_parent_message,
            ),
            message_signature("obf_child", declared_field_signatures=[], dump_cs_msg=obf_child_message),
        ],
        non_obf_signatures=[
            message_signature(
                "ClearParent",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                dump_cs_msg=clear_parent_message,
            ),
            message_signature("ClearChild", declared_field_signatures=[], dump_cs_msg=clear_child_message),
            message_signature("OtherClear", declared_field_signatures=[], dump_cs_msg=other_clear_message),
        ],
        obf_messages_by_cls=build_message_lookup([obf_parent_message, obf_child_message]),
        non_obf_messages_by_cls=build_message_lookup(
            [clear_parent_message, clear_child_message, other_clear_message]
        ),
    )


def select_best_for_test(
    *,
    obf_signatures: list[MessageAccessSignature],
    non_obf_signatures: list[MessageAccessSignature],
    scores_matrix: np.ndarray,
    roots_only: bool,
) -> SelectedSignaturePair | None:
    workspace = build_matching_workspace(
        obf_signatures=obf_signatures,
        non_obf_signatures=non_obf_signatures,
        obf_messages_by_cls={},
        non_obf_messages_by_cls={},
    )
    return select_best_signature_pair(
        workspace=workspace,
        scores_matrix=scores_matrix,
        available_non_obf=list(workspace.non_obf_signatures),
        available_obf=list(workspace.obf_signatures),
        roots_only=roots_only,
        pinned_pairs_config=build_verified_mapping(),
    )


def select_best_signature_pair(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
    available_non_obf: Sequence[MessageAccessSignature],
    available_obf: Sequence[MessageAccessSignature],
    roots_only: bool,
    pinned_pairs_config: PinnedPairsConfig,
) -> SelectedSignaturePair | None:
    """Take only the top pair. Production drains the whole batch; tests assert on one."""
    selected_pairs = select_signature_pairs(
        workspace=workspace,
        scores_matrix=scores_matrix,
        available_non_obf_indexes={
            workspace.signature_indexes.non_obf_index_by_cls[signature.message_cls]
            for signature in available_non_obf
        },
        available_obf_indexes={
            workspace.signature_indexes.obf_index_by_cls[signature.message_cls] for signature in available_obf
        },
        roots_only=roots_only,
        pinned_pairs_config=pinned_pairs_config,
    )
    return selected_pairs[0] if selected_pairs else None


def select_grouped_matches_for_test(
    *,
    workspace: MatchingWorkspace,
    prepared_scores: PreparedScoreData,
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    runtime_data_store: RuntimeDataStore,
    pinned_pairs_config: PinnedPairsConfig,
    capture_sequence_hints_config: CaptureSequenceHintsConfig,
    signature_overrides_by_non_obf_cls: dict[str, SignatureOverrideEntry] | None = None,
    obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
    non_obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
) -> tuple[MatchResult, ...]:
    """Assemble the two bundles from the loose pieces a test naturally has to hand."""
    return select_grouped_matches(
        workspace=workspace,
        prepared_scores=prepared_scores,
        inputs=MatchingInputs(
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            obf_signatures_by_cls=dict(workspace.obf_signatures_by_cls),
            non_obf_signatures_by_cls=dict(workspace.non_obf_signatures_by_cls),
            signature_overrides_by_non_obf_cls=signature_overrides_by_non_obf_cls or {},
            obf_enum_signatures_by_name=obf_enum_signatures_by_name or {},
            non_obf_enum_signatures_by_name=non_obf_enum_signatures_by_name or {},
            obf_access_trace=obf_access_trace,
            non_obf_access_trace=non_obf_access_trace,
        ),
        run_config=MatchingRunConfig(
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=pinned_pairs_config,
            capture_sequence_hints_config=capture_sequence_hints_config,
        ),
    )


def match_messages_for_test(
    obf_signatures: list[MessageAccessSignature],
    non_obf_signatures: list[MessageAccessSignature],
    *,
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    runtime_data_store: RuntimeDataStore,
    pinned_pairs_config: PinnedPairsConfig,
    capture_sequence_hints_config: CaptureSequenceHintsConfig,
    signature_overrides_by_non_obf_cls: dict[str, SignatureOverrideEntry] | None = None,
    obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
    non_obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
) -> tuple[MatchResult, ...]:
    """Keep tests writing two signature lists; production passes the loaded bundle instead."""
    return match_messages(
        inputs=MatchingInputs(
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            obf_signatures_by_cls={signature.message_cls: signature for signature in obf_signatures},
            non_obf_signatures_by_cls={signature.message_cls: signature for signature in non_obf_signatures},
            signature_overrides_by_non_obf_cls=signature_overrides_by_non_obf_cls or {},
            obf_enum_signatures_by_name=obf_enum_signatures_by_name or {},
            non_obf_enum_signatures_by_name=non_obf_enum_signatures_by_name or {},
            obf_access_trace=obf_access_trace,
            non_obf_access_trace=non_obf_access_trace,
        ),
        run_config=MatchingRunConfig(
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=pinned_pairs_config,
            capture_sequence_hints_config=capture_sequence_hints_config,
        ),
    )


def build_prepared_scores_for_test(
    *,
    workspace: MatchingWorkspace,
    obf_messages_by_cls: dict[str, DumpCSMessage],
    non_obf_messages_by_cls: dict[str, DumpCSMessage],
    runtime_data_store: RuntimeDataStore,
    pinned_pairs_config: PinnedPairsConfig,
    signature_overrides_by_non_obf_cls: dict[str, SignatureOverrideEntry] | None = None,
    obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    non_obf_enum_signatures_by_name: dict[str, EnumSignatureEntry] | None = None,
    obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
    non_obf_access_trace: AccessTraceDocument = EMPTY_ACCESS_TRACE,
) -> PreparedScoreData:
    return build_prepared_scores(
        workspace=workspace,
        inputs=MatchingInputs(
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            obf_signatures_by_cls=dict(workspace.obf_signatures_by_cls),
            non_obf_signatures_by_cls=dict(workspace.non_obf_signatures_by_cls),
            signature_overrides_by_non_obf_cls=signature_overrides_by_non_obf_cls or {},
            obf_enum_signatures_by_name=obf_enum_signatures_by_name or {},
            non_obf_enum_signatures_by_name=non_obf_enum_signatures_by_name or {},
            obf_access_trace=obf_access_trace,
            non_obf_access_trace=non_obf_access_trace,
        ),
        run_config=MatchingRunConfig(
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=pinned_pairs_config,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        ),
    )
