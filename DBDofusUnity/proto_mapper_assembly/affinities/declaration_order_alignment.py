import re
from collections import defaultdict
from collections.abc import Mapping

import numpy as np

from DBDofusUnity.proto_mapper_assembly.affinities._group_similarity import build_group_scores_matrix, match_groups
from DBDofusUnity.proto_mapper_assembly.affinities._sequence_alignment import align_sequences_monotonically
from DBDofusUnity.proto_mapper_assembly.interfaces.affinity import AffinityResult, AffinitySignalInputs
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument

_OBFUSCATED_METHOD_PATTERN = re.compile(r"^([a-z]+)::.*?\s([a-z]+)\(")
"""Only generated wrappers rename both owner and method to sequential lowercase identifiers."""

_ALPHABET_SIZE = 26
_MIN_SEGMENT_SIZE = 3
_MAX_SEGMENT_GAP = 6

_MIN_SEGMENT_MATCH_SCORE = 0.0
_MIN_SEGMENT_MATCH_MARGIN = 0.10

_SEGMENT_MEMBER_GAP_PENALTY = -0.05
_SEGMENT_MEMBER_FALLBACK_AFFINITY = 0.9
"""Keep unaligned segment members competitive because adjacent wrappers can swap order."""


def build_declaration_order_affinity(signal_inputs: AffinitySignalInputs, /) -> AffinityResult:
    """Return affinity and mask from wrapper declaration order, which survives obfuscation."""
    workspace = signal_inputs.workspace
    obf_access_trace = signal_inputs.obf_access_trace
    non_obf_access_trace = signal_inputs.non_obf_access_trace
    base_scores_matrix = signal_inputs.base_scores_matrix

    non_obf_segments = _build_declaration_segments(
        access_trace=non_obf_access_trace,
        index_by_cls=workspace.signature_indexes.non_obf_index_by_cls,
    )
    obf_segments = _build_declaration_segments(
        access_trace=obf_access_trace,
        index_by_cls=workspace.signature_indexes.obf_index_by_cls,
    )
    non_obf_count, obf_count = base_scores_matrix.shape
    if not non_obf_segments or not obf_segments:
        return AffinityResult(
            np.zeros_like(base_scores_matrix),
            np.zeros((non_obf_count, obf_count), dtype=bool),
        )

    matched_segments = match_groups(
        group_scores_matrix=build_group_scores_matrix(
            base_scores_matrix=base_scores_matrix,
            non_obf_groups=non_obf_segments,
            obf_groups=obf_segments,
        ),
        min_score=_MIN_SEGMENT_MATCH_SCORE,
        min_margin=_MIN_SEGMENT_MATCH_MARGIN,
    )

    affinity_matrix = np.zeros_like(base_scores_matrix)
    applicable_mask = np.zeros((non_obf_count, obf_count), dtype=bool)
    for non_obf_segment_index, obf_segment_index in matched_segments:
        non_obf_members = non_obf_segments[non_obf_segment_index]
        obf_members = obf_segments[obf_segment_index]
        applicable_mask[np.ix_(non_obf_members, obf_members)] = True
        affinity_matrix[np.ix_(non_obf_members, obf_members)] = _SEGMENT_MEMBER_FALLBACK_AFFINITY
        aligned_pairs = align_sequences_monotonically(
            non_obf_indexes=non_obf_members,
            obf_indexes=obf_members,
            scores_matrix=base_scores_matrix,
            gap_penalty=_SEGMENT_MEMBER_GAP_PENALTY,
        )
        for non_obf_index, obf_index in aligned_pairs:
            affinity_matrix[non_obf_index, obf_index] = 1.0
    return AffinityResult(affinity_matrix, applicable_mask)


def _build_declaration_segments(
    *,
    access_trace: AccessTraceDocument,
    index_by_cls: Mapping[str, int],
) -> tuple[tuple[int, ...], ...]:
    message_index_by_alias_by_owner: dict[str, dict[str, int]] = defaultdict(dict)
    for traced_function in access_trace.functions_by_address.values():
        touched_classes = {access_entry.cls for access_entry in traced_function.access_infos}
        if len(touched_classes) != 1:
            # Multi-message wrappers do not establish a unique declaration position.
            continue
        message_cls = next(iter(touched_classes))
        message_index = index_by_cls.get(message_cls)
        if message_index is None:
            continue
        for alias in traced_function.aliases:
            matched = _OBFUSCATED_METHOD_PATTERN.match(alias.name)
            if matched is None:
                continue
            message_index_by_alias_by_owner[matched.group(1)][matched.group(2)] = message_index

    segments: list[tuple[int, ...]] = []
    for message_index_by_alias in message_index_by_alias_by_owner.values():
        segments.extend(_split_into_segments(message_index_by_alias))
    return tuple(segments)


def _split_into_segments(message_index_by_alias: Mapping[str, int]) -> list[tuple[int, ...]]:
    """Group aliases by length: base-26 ordering does not cross identifier lengths."""
    by_alias_length: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for alias, message_index in message_index_by_alias.items():
        by_alias_length[len(alias)].append((_alias_ordinal(alias), message_index))

    segments: list[tuple[int, ...]] = []
    for ordered_aliases in by_alias_length.values():
        current_segment: list[int] = []
        previous_ordinal: int | None = None
        for alias_ordinal, message_index in sorted(ordered_aliases):
            if previous_ordinal is not None and alias_ordinal - previous_ordinal > _MAX_SEGMENT_GAP:
                segments.append(tuple(current_segment))
                current_segment = []
            previous_ordinal = alias_ordinal
            if message_index not in current_segment:
                current_segment.append(message_index)
        segments.append(tuple(current_segment))
    return [segment for segment in segments if len(segment) >= _MIN_SEGMENT_SIZE]


def _alias_ordinal(alias: str) -> int:
    ordinal = 0
    for character in alias:
        ordinal = ordinal * _ALPHABET_SIZE + (ord(character) - ord("a"))
    return ordinal
