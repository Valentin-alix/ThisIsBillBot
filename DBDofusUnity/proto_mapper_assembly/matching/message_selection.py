import numpy as np
from tqdm import tqdm

from DBDofusUnity.proto_mapper_assembly.field_mapping.field_mapper import build_field_mapping
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import FieldMappingContext
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace, MatchResult, PreparedScoreData
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from DBDofusUnity.proto_mapper_assembly.matching.pair_selection import (
    SelectedSignaturePair,
    select_signature_pairs,
)
from DBDofusUnity.proto_mapper_assembly.matching.score_constraints import build_adjusted_scores_matrix
from DBDofusUnity.proto_mapper_assembly.matching.score_lookup import build_lazy_score_by_pair_lookup_from_signatures
from DBDofusUnity.proto_mapper_assembly.scoring.message_scoring import (
    StructureSimilarityContext,
    pair_evidence_coverage,
)


def match_all_signatures_iteratively(
    *,
    workspace: MatchingWorkspace,
    prepared_scores: PreparedScoreData,
    matching_store: IterativeMatchingStore,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
) -> list[MatchResult]:
    """Match roots first so confirmed parents constrain nested candidates."""
    available_non_obf_indexes = {
        index
        for index, signature in enumerate(workspace.non_obf_signatures)
        if signature.message_cls not in matching_store.confirmed_obf_by_non_obf
    }
    available_obf_indexes = {
        index
        for index, signature in enumerate(workspace.obf_signatures)
        if signature.message_cls not in matching_store.confirmed_non_obf_by_obf
    }
    field_mapping_score_by_pair = build_lazy_score_by_pair_lookup_from_signatures(
        obf_signatures_by_cls=workspace.obf_signatures_by_cls,
        non_obf_signatures_by_cls=workspace.non_obf_signatures_by_cls,
        structure_context=StructureSimilarityContext(
            left_signatures_by_cls=workspace.obf_signatures_by_cls,
            right_signatures_by_cls=workspace.non_obf_signatures_by_cls,
            left_enum_signatures_by_name=inputs.obf_enum_signatures_by_name,
            right_enum_signatures_by_name=inputs.non_obf_enum_signatures_by_name,
            left_access_trace=inputs.obf_access_trace,
            right_access_trace=inputs.non_obf_access_trace,
        ),
    )
    field_mapping_context = FieldMappingContext(
        score_by_pair=field_mapping_score_by_pair,
        runtime_data_store=run_config.runtime_data_store,
        signature_overrides_by_non_obf_cls=inputs.signature_overrides_by_non_obf_cls,
        obf_enum_signatures_by_name=inputs.obf_enum_signatures_by_name,
        non_obf_enum_signatures_by_name=inputs.non_obf_enum_signatures_by_name,
        obf_access_trace=inputs.obf_access_trace,
        non_obf_access_trace=inputs.non_obf_access_trace,
    )

    capture_order_index = CaptureOrderIndex.build(
        workspace=workspace,
        pinned_pairs_config=run_config.pinned_pairs_config,
        runtime_data_store=run_config.runtime_data_store,
    )

    matches: list[MatchResult] = []
    for roots_only in (True, False):
        matches.extend(
            match_signatures_iteratively(
                workspace=workspace,
                prepared_scores=prepared_scores,
                matching_store=matching_store,
                inputs=inputs,
                run_config=run_config,
                field_mapping_context=field_mapping_context,
                capture_order_index=capture_order_index,
                available_non_obf_indexes=available_non_obf_indexes,
                available_obf_indexes=available_obf_indexes,
                roots_only=roots_only,
            )
        )
    return matches


def match_signatures_iteratively(
    *,
    workspace: MatchingWorkspace,
    prepared_scores: PreparedScoreData,
    matching_store: IterativeMatchingStore,
    inputs: MatchingInputs,
    run_config: MatchingRunConfig,
    field_mapping_context: FieldMappingContext,
    capture_order_index: CaptureOrderIndex,
    available_non_obf_indexes: set[int],
    available_obf_indexes: set[int],
    roots_only: bool,
) -> list[MatchResult]:
    matches: list[MatchResult] = []
    cached_adjusted_matrix: np.ndarray | None = None
    cached_store_version: int = -1
    selected_pair_queue: list[SelectedSignaturePair] = []
    progress_desc = f"matching messages ({'roots' if roots_only else 'all'})"
    with tqdm(total=len(available_non_obf_indexes), desc=progress_desc) as progress_bar:
        while available_non_obf_indexes and available_obf_indexes:
            remaining_before = len(available_non_obf_indexes)
            if not selected_pair_queue:
                if cached_adjusted_matrix is None or matching_store.version != cached_store_version:
                    cached_adjusted_matrix = build_adjusted_scores_matrix(
                        workspace=workspace,
                        base_scores_matrix=prepared_scores.final_scores_matrix,
                        matching_store=matching_store,
                        capture_order_index=capture_order_index,
                        capture_sequence_hints_config=run_config.capture_sequence_hints_config,
                    )
                    cached_store_version = matching_store.version
                selected_pair_queue.extend(
                    select_signature_pairs(
                        workspace=workspace,
                        scores_matrix=cached_adjusted_matrix,
                        available_non_obf_indexes=available_non_obf_indexes,
                        available_obf_indexes=available_obf_indexes,
                        roots_only=roots_only,
                        pinned_pairs_config=run_config.pinned_pairs_config,
                    )
                )
                if not selected_pair_queue:
                    break
            selected_pair = selected_pair_queue.pop(0)

            if (
                selected_pair.non_obf_index not in available_non_obf_indexes
                or selected_pair.obf_index not in available_obf_indexes
            ):
                continue

            if not matching_store.register_confirmed(
                obf_message_cls=selected_pair.obf_signature.message_cls,
                non_obf_message_cls=selected_pair.non_obf_signature.message_cls,
                source="global_match",
            ):
                available_non_obf_indexes.remove(selected_pair.non_obf_index)
                available_obf_indexes.remove(selected_pair.obf_index)
                progress_bar.update(remaining_before - len(available_non_obf_indexes))
                continue

            field_mapping_result = build_field_mapping(
                non_obf_signature=selected_pair.non_obf_signature,
                obf_signature=selected_pair.obf_signature,
                non_obf_messages_by_cls=inputs.non_obf_messages_by_cls,
                obf_messages_by_cls=inputs.obf_messages_by_cls,
                matching_store=matching_store,
                field_mapping_context=field_mapping_context,
                obf_type_index=workspace.obf_type_index,
                non_obf_type_index=workspace.non_obf_type_index,
                pinned_pair=selected_pair.pinned_pair,
            )
            for discovery in field_mapping_result.discovered_message_matches:
                matching_store.register_inferred(discovery)
            if field_mapping_result.discovered_message_matches:
                selected_pair_queue.clear()

            non_obf_index = selected_pair.non_obf_index
            obf_index = selected_pair.obf_index
            pair_key = MatchPairKey(
                selected_pair.obf_signature.message_cls, selected_pair.non_obf_signature.message_cls
            )
            file_descriptor_similarity = prepared_scores.file_descriptor_similarity_by_pair[
                selected_pair.non_obf_signature.file_descriptor, selected_pair.obf_signature.file_descriptor
            ]
            matches.append(
                MatchResult(
                    non_obf_signature=selected_pair.non_obf_signature,
                    obf_signature=selected_pair.obf_signature,
                    score=selected_pair.score,
                    group_similarity_score=file_descriptor_similarity,
                    assembly_similarity_score=float(
                        prepared_scores.assembly_scores_matrix[non_obf_index, obf_index]
                    ),
                    structure_similarity_score=float(
                        prepared_scores.structure_scores_matrix[non_obf_index, obf_index]
                    ),
                    field_mapping=field_mapping_result.field_mapping,
                    field_mapping_infos=field_mapping_result.field_mapping_infos,
                    runtime_confidence=prepared_scores.runtime_confidence_by_pair.get(pair_key),
                    field_mapping_rejected_infos=field_mapping_result.field_mapping_rejected_infos,
                    field_mapping_unmapped_non_obf_fields=field_mapping_result.field_mapping_unmapped_non_obf_fields,
                    match_margin=selected_pair.match_margin,
                    runner_up_obf=selected_pair.runner_up_obf,
                    is_low_confidence=False,
                    evidence_coverage=pair_evidence_coverage(
                        selected_pair.obf_signature, selected_pair.non_obf_signature
                    ),
                    is_runtime_observed=run_config.runtime_data_store.has_capture_for_obf_message(
                        message=inputs.obf_messages_by_cls[selected_pair.obf_signature.message_cls],
                        obf_messages_by_cls=inputs.obf_messages_by_cls,
                    ),
                )
            )
            available_non_obf_indexes.remove(selected_pair.non_obf_index)
            available_obf_indexes.remove(selected_pair.obf_index)
            progress_bar.update(remaining_before - len(available_non_obf_indexes))
    return matches
