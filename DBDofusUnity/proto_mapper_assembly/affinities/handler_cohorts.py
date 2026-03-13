from collections.abc import Mapping

import numpy as np

from DBDofusUnity.proto_mapper_assembly.affinities._group_similarity import build_group_scores_matrix, match_groups
from DBDofusUnity.proto_mapper_assembly.affinities._sequence_alignment import align_sequences_monotonically
from DBDofusUnity.proto_mapper_assembly.interfaces.affinity import AffinityResult, AffinitySignalInputs
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import (
    AccessTraceDocument,
    HandlerRegistrationAccessEntry,
)

_MIN_COHORT_ASSIGNMENT_SCORE = 0.0
_MIN_COHORT_ASSIGNMENT_MARGIN = 0.10
_COHORT_ALIGNMENT_GAP_PENALTY = -0.05
_UNALIGNED_COHORT_MEMBER_AFFINITY = 0.8
_MIN_COHORT_LENGTH_RATIO = 0.9


def build_handler_cohort_affinity(signal_inputs: AffinitySignalInputs, /) -> AffinityResult:
    """Return cohort affinity and mask; missing registration evidence must leave scores unchanged."""
    workspace = signal_inputs.workspace
    obf_access_trace = signal_inputs.obf_access_trace
    non_obf_access_trace = signal_inputs.non_obf_access_trace
    base_scores_matrix = signal_inputs.base_scores_matrix

    non_obf_cohorts = _build_cohort_member_indexes(
        access_trace=non_obf_access_trace,
        index_by_cls=workspace.signature_indexes.non_obf_index_by_cls,
    )
    obf_cohorts = _build_cohort_member_indexes(
        access_trace=obf_access_trace,
        index_by_cls=workspace.signature_indexes.obf_index_by_cls,
    )
    non_obf_count, obf_count = base_scores_matrix.shape
    if not non_obf_cohorts or not obf_cohorts:
        return AffinityResult(
            np.zeros_like(base_scores_matrix),
            np.zeros((non_obf_count, obf_count), dtype=bool),
        )

    matched_cohorts = match_groups(
        group_scores_matrix=build_group_scores_matrix(
            base_scores_matrix=base_scores_matrix,
            non_obf_groups=non_obf_cohorts,
            obf_groups=obf_cohorts,
        ),
        min_score=_MIN_COHORT_ASSIGNMENT_SCORE,
        min_margin=_MIN_COHORT_ASSIGNMENT_MARGIN,
    )
    affinity_matrix = _build_cohort_alignment_affinity(
        non_obf_cohorts=non_obf_cohorts,
        obf_cohorts=obf_cohorts,
        matched_cohorts=matched_cohorts,
        base_scores_matrix=base_scores_matrix,
    )

    # Mask each confidently placed side, including cross-cohort pairs, to penalize crossings.
    non_obf_is_matched = np.zeros(non_obf_count, dtype=bool)
    obf_is_matched = np.zeros(obf_count, dtype=bool)
    for non_obf_cohort_index, obf_cohort_index in matched_cohorts:
        non_obf_is_matched[list(non_obf_cohorts[non_obf_cohort_index])] = True
        obf_is_matched[list(obf_cohorts[obf_cohort_index])] = True
    return AffinityResult(affinity_matrix, non_obf_is_matched[:, None] & obf_is_matched[None, :])


def _build_cohort_alignment_affinity(
    *,
    non_obf_cohorts: tuple[tuple[int, ...], ...],
    obf_cohorts: tuple[tuple[int, ...], ...],
    matched_cohorts: tuple[tuple[int, int], ...],
    base_scores_matrix: np.ndarray,
) -> np.ndarray:
    """Use registration order to break sibling ties while preserving the cohort membership reward."""
    affinity_matrix = np.zeros_like(base_scores_matrix)
    for non_obf_cohort_index, obf_cohort_index in matched_cohorts:
        non_obf_members = non_obf_cohorts[non_obf_cohort_index]
        obf_members = obf_cohorts[obf_cohort_index]
        is_alignable = min(len(non_obf_members), len(obf_members)) >= _MIN_COHORT_LENGTH_RATIO * max(
            len(non_obf_members), len(obf_members)
        )
        affinity_matrix[np.ix_(non_obf_members, obf_members)] = (
            _UNALIGNED_COHORT_MEMBER_AFFINITY if is_alignable else 1.0
        )
        if not is_alignable:
            continue
        aligned_pairs = align_sequences_monotonically(
            non_obf_indexes=non_obf_members,
            obf_indexes=obf_members,
            scores_matrix=base_scores_matrix,
            gap_penalty=_COHORT_ALIGNMENT_GAP_PENALTY,
        )
        for non_obf_index, obf_index in aligned_pairs:
            affinity_matrix[non_obf_index, obf_index] = 1.0
    return affinity_matrix


def _build_cohort_member_indexes(
    *,
    access_trace: AccessTraceDocument,
    index_by_cls: Mapping[str, int],
) -> tuple[tuple[int, ...], ...]:
    cohorts: list[tuple[int, ...]] = []
    for traced_function in access_trace.functions_by_address.values():
        ordered_members = sorted(
            {
                (access_entry.registration_ordinal, index_by_cls[access_entry.cls])
                for access_entry in traced_function.access_infos
                if isinstance(access_entry, HandlerRegistrationAccessEntry)
                and access_entry.cls in index_by_cls
            }
        )
        member_indexes = dict.fromkeys(member_index for _, member_index in ordered_members)
        if member_indexes:
            cohorts.append(tuple(member_indexes))
    return tuple(cohorts)
