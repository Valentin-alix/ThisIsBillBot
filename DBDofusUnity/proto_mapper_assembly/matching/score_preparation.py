from __future__ import annotations

from collections.abc import Mapping

import numpy as np
from proto_mapper_assembly.affinities.callee_affinity import build_callee_affinity
from proto_mapper_assembly.affinities.declaration_order_alignment import build_declaration_order_affinity
from proto_mapper_assembly.affinities.file_descriptor_similarity import build_file_descriptor_similarity
from proto_mapper_assembly.affinities.handler_cohorts import build_handler_cohort_affinity
from proto_mapper_assembly.controllers.access_signatures import count_handler_registrations_by_cls
from proto_mapper_assembly.interfaces.affinity import AffinitySignalInputs, MaskedAffinitySignal
from proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.matching import (
    MatchingWorkspace,
    PreparedScoreData,
)
from proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from proto_mapper_assembly.matching.runtime_rescore import build_runtime_rescored_scores
from proto_mapper_assembly.matching.static_scores import (
    apply_pinned_pair_overrides_around_prospective_mask,
    build_static_score_data,
)
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from proto_mapper_assembly.scoring.message_scoring import StructureSimilarityContext

_FILE_DESCRIPTOR_SIMILARITY_WEIGHT = 0.5
_HANDLER_REGISTRATION_SIMILARITY_WEIGHT = 0.25

_MASKED_AFFINITY_SIGNALS: tuple[MaskedAffinitySignal, ...] = (
    MaskedAffinitySignal(
        name="handler_cohort",
        weight=0.10,
        build=build_handler_cohort_affinity,
        rationale=(
            "Cohorts survive a rebuild near-perfectly but not perfectly, so crossing one must cost "
            "score without ever becoming unreachable."
        ),
    ),
    MaskedAffinitySignal(
        name="declaration_order",
        weight=0.15,
        build=build_declaration_order_affinity,
        rationale=(
            "A little above the cohorts: the declaration slot is the only thing separating messages "
            "with no distinguishing structure of their own. Still a blend, since adjacent wrappers "
            "do occasionally swap places between builds."
        ),
    ),
    MaskedAffinitySignal(
        name="callee",
        weight=0.15,
        build=build_callee_affinity,
        rationale=(
            "For the messages nothing else reaches: no fields or one, shape shared with dozens of "
            "candidates. What their code calls into is the only thing left, and obfuscation leaves "
            "it alone."
        ),
    ),
)
# Blend order is intentional: each signal rescales the running matrix and uses a different
# applicability mask. File-descriptor and handler-registration evidence stay outside this table
# because the former is unmasked and returns metadata, while the latter affects runtime candidate
# selection.


def build_prepared_scores(
    *,
    workspace: MatchingWorkspace,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
) -> PreparedScoreData:
    """
    Build the final score matrix from static, runtime, and corpus-level evidence.

    Compute static scores, blend handler-registration evidence, rescore runtime-backed candidates,
    then apply file-descriptor and masked affinity signals in order. Affinities are derived from the
    static matrix and blended sequentially into the running matrix. Apply prospective constraints
    and pins last so hard overrides survive every soft scoring step.
    """
    structure_context = _build_structure_similarity_context(workspace=workspace, inputs=inputs)
    static_score_data = build_static_score_data(
        obf_signatures=workspace.obf_signatures,
        non_obf_signatures=workspace.non_obf_signatures,
        pinned_pairs_config=run_config.pinned_pairs_config,
        runtime_data_store=run_config.runtime_data_store,
        structure_context=structure_context,
    )
    handler_adjusted_scores_matrix = _blend_handler_registration_similarity(
        workspace=workspace,
        scores_matrix=static_score_data.static_scores_matrix,
        obf_messages_by_cls=inputs.obf_messages_by_cls,
        runtime_data_store=run_config.runtime_data_store,
        obf_access_trace=inputs.obf_access_trace,
        non_obf_access_trace=inputs.non_obf_access_trace,
    )
    final_scores_matrix, runtime_confidence_by_pair = build_runtime_rescored_scores(
        workspace=workspace,
        inputs=inputs,
        run_config=run_config,
        scores_matrix=handler_adjusted_scores_matrix,
        structure_scores_matrix=static_score_data.structure_scores_matrix,
    )

    file_descriptor_similarity_matrix, file_descriptor_similarity_by_pair = build_file_descriptor_similarity(
        workspace=workspace, base_scores_matrix=static_score_data.static_scores_matrix
    )
    final_scores_matrix = _blend_file_descriptor_similarity(
        message_scores_matrix=final_scores_matrix,
        file_descriptor_similarity_matrix=file_descriptor_similarity_matrix,
    )
    signal_inputs = AffinitySignalInputs(
        workspace=workspace,
        base_scores_matrix=static_score_data.static_scores_matrix,
        obf_access_trace=inputs.obf_access_trace,
        non_obf_access_trace=inputs.non_obf_access_trace,
    )
    for signal in _MASKED_AFFINITY_SIGNALS:
        affinity_matrix, applicable_mask = signal.build(signal_inputs)
        final_scores_matrix = _blend_masked_affinity(
            message_scores_matrix=final_scores_matrix,
            affinity_matrix=affinity_matrix,
            applicable_mask=applicable_mask,
            weight=signal.weight,
        )
    final_scores_matrix = apply_pinned_pair_overrides_around_prospective_mask(
        workspace=workspace,
        scores_matrix=final_scores_matrix,
        pinned_pairs_config=run_config.pinned_pairs_config,
    )

    return PreparedScoreData(
        final_scores_matrix=final_scores_matrix,
        structure_scores_matrix=static_score_data.structure_scores_matrix,
        assembly_scores_matrix=static_score_data.assembly_scores_matrix,
        runtime_confidence_by_pair=runtime_confidence_by_pair,
        file_descriptor_similarity_by_pair=file_descriptor_similarity_by_pair,
    )


def _blend_handler_registration_similarity(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
    obf_messages_by_cls: Mapping[str, DumpCSMessage],
    runtime_data_store: RuntimeDataStore,
    obf_access_trace: AccessTraceDocument,
    non_obf_access_trace: AccessTraceDocument,
) -> np.ndarray:
    """
    Blend handler-registration-count similarity into viable server-message pairs.

    Apply the signal only to positive Event/Response candidates whose obfuscated message was
    observed from the server and whose registration counts are known on both sides.
    """
    adjusted_scores_matrix = np.array(scores_matrix, copy=True)
    obf_registration_count_by_cls = count_handler_registrations_by_cls(obf_access_trace)
    non_obf_registration_count_by_cls = count_handler_registrations_by_cls(non_obf_access_trace)
    for obf_index, obf_signature in enumerate(workspace.obf_signatures):
        obf_registration_count = obf_registration_count_by_cls.get(obf_signature.message_cls)
        if obf_registration_count is None:
            continue
        runtime_instances = runtime_data_store.get_normalized_content_for_obf_message(
            message=obf_messages_by_cls[obf_signature.message_cls],
            obf_messages_by_cls=obf_messages_by_cls,
        )
        if not any(runtime_instance.get("from_server") is True for runtime_instance in runtime_instances):
            continue
        for non_obf_index, non_obf_signature in enumerate(workspace.non_obf_signatures):
            if not non_obf_signature.message_cls.endswith(("Event", "Response")):
                continue
            non_obf_registration_count = non_obf_registration_count_by_cls.get(non_obf_signature.message_cls)
            if non_obf_registration_count is None:
                continue
            current_score = float(scores_matrix[non_obf_index, obf_index])
            if current_score <= 0.0:
                continue
            registration_similarity = min(obf_registration_count, non_obf_registration_count) / max(
                obf_registration_count, non_obf_registration_count
            )
            adjusted_scores_matrix[non_obf_index, obf_index] = (
                1.0 - _HANDLER_REGISTRATION_SIMILARITY_WEIGHT
            ) * current_score + _HANDLER_REGISTRATION_SIMILARITY_WEIGHT * registration_similarity
    return adjusted_scores_matrix


def _build_structure_similarity_context(
    *, workspace: MatchingWorkspace, inputs: MatchingInputs
) -> StructureSimilarityContext:
    return StructureSimilarityContext(
        left_signatures_by_cls=workspace.obf_signatures_by_cls,
        right_signatures_by_cls=workspace.non_obf_signatures_by_cls,
        left_enum_signatures_by_name=dict(inputs.obf_enum_signatures_by_name),
        right_enum_signatures_by_name=dict(inputs.non_obf_enum_signatures_by_name),
        left_access_trace=inputs.obf_access_trace,
        right_access_trace=inputs.non_obf_access_trace,
    )


def _blend_file_descriptor_similarity(
    *, message_scores_matrix: np.ndarray, file_descriptor_similarity_matrix: np.ndarray
) -> np.ndarray:
    """
    Blend file-descriptor alignment into every candidate score.

    The signal is intentionally unmasked so it can revive pairs rejected by static scoring gates.
    Restricting it to positive static scores preserved accuracy but removed 26 mappings.
    """
    return (
        1.0 - _FILE_DESCRIPTOR_SIMILARITY_WEIGHT
    ) * message_scores_matrix + _FILE_DESCRIPTOR_SIMILARITY_WEIGHT * file_descriptor_similarity_matrix


def _blend_masked_affinity(
    *,
    message_scores_matrix: np.ndarray,
    affinity_matrix: np.ndarray,
    applicable_mask: np.ndarray,
    weight: float,
) -> np.ndarray:
    """
    Blend an affinity into applicable cells and leave all others unchanged.

    The bounded blend can penalize disagreement without zeroing an existing score. Cells outside
    the mask remain unchanged because missing affinity evidence is neutral.
    """
    blended_scores_matrix = (1.0 - weight) * message_scores_matrix + weight * affinity_matrix
    return np.where(applicable_mask, blended_scores_matrix, message_scores_matrix)
