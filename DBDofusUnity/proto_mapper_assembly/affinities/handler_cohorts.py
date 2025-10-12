from __future__ import annotations

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
"""Swept against the full pipeline: below this the cohort assignment gets noisy, above it the
constraint stops firing on cohorts that are in fact well placed."""
_COHORT_ALIGNMENT_GAP_PENALTY = -0.05
"""Deliberately small: cohorts differ by a handful of added or removed handlers, so the alignment
should pair members up wherever it can and only spend gaps on the genuine length difference."""
_UNALIGNED_COHORT_MEMBER_AFFINITY = 0.8
"""Kept high: belonging to the same matched cohort is the primary evidence, the ordinal alignment
only tips the balance between siblings it cannot otherwise separate."""
_MIN_COHORT_LENGTH_RATIO = 0.9
"""Below this the two cohorts differ by too many handlers for their ordinals to line up, so the
alignment is skipped and membership alone is rewarded, as it was before ordering existed."""


def build_handler_cohort_affinity(signal_inputs: AffinitySignalInputs, /) -> AffinityResult:
    """
    Align handler-registration cohorts across builds, then expose the resulting message affinity.

    Messages whose handlers are registered by a single Core.dll function keep that grouping across
    builds even though every name, offset and tag around them is shuffled. Cohorts are therefore
    matched against each other first (Hungarian assignment over the message scores they already
    contain), and the matched cohorts then constrain the messages inside them.

    Returns ``(affinity_matrix, applicable_mask)``, both shaped like ``base_scores_matrix``. The
    mask is only set for pairs where *both* messages belong to a cohort; everywhere else the caller
    must leave the score untouched, since the absence of a registration is not evidence.
    """
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

    # Only messages whose own cohort was confidently placed may be constrained: a message sitting in
    # an ambiguous cohort must keep its score, otherwise a bad cohort assignment silently penalizes
    # the correct pair. Note this is per side, not per pair -- a message in one matched cohort paired
    # with a message in *another* matched cohort is masked in, and its zero affinity is what makes
    # crossing cohorts cost score.
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
    """
    Grade the pairs inside a matched cohort by whether they also line up in registration order.

    Sharing a matched cohort is already strong evidence, so it keeps most of its reward; what
    membership alone cannot do is separate two same-shaped siblings registered side by side.
    Registrations are emitted in source order on both builds, so the ordinal alignment singles out
    one obfuscated member per non-obfuscated one and gives it the edge.

    Missing the alignment must stay cheap: cohorts gain and lose handlers between builds, and the
    order around an insertion is genuinely ambiguous. Demoting an unaligned member all the way to a
    cohort-crossing score would throw away the membership evidence that is usually right.
    """
    affinity_matrix = np.zeros_like(base_scores_matrix)
    for non_obf_cohort_index, obf_cohort_index in matched_cohorts:
        non_obf_members = non_obf_cohorts[non_obf_cohort_index]
        obf_members = obf_cohorts[obf_cohort_index]
        is_alignable = min(len(non_obf_members), len(obf_members)) >= _MIN_COHORT_LENGTH_RATIO * max(
            len(non_obf_members), len(obf_members)
        )
        # Without a trustworthy order every member of the cohort stays on equal footing, which is
        # how this signal behaved before ordering existed.
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
    """
    Return, per registering function, the score-matrix indexes of the messages it registers.

    Members keep their ``registration_ordinal`` order rather than being sorted by matrix index: that
    ordinal is the source order of the registrations, and it survives obfuscation, so it is what lets
    two members of the same cohort be told apart.
    """
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
        # A message registered twice in the same function keeps only its first ordinal, so the
        # sequence stays a plain list of distinct members that the alignment can walk through.
        member_indexes = dict.fromkeys(member_index for _, member_index in ordered_members)
        if member_indexes:
            cohorts.append(tuple(member_indexes))
    return tuple(cohorts)
