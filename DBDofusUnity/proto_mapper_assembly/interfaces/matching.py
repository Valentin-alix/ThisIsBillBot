from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property

import numpy as np

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.field_mapping import (
    FieldMappingInfos,
    FieldMappingRejectedInfos,
    FieldMappingUnmappedNonObfFields,
)
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey


@dataclass(frozen=True)
class SignatureIndexLookup:
    obf_index_by_cls: dict[str, int]
    non_obf_index_by_cls: dict[str, int]


@dataclass(frozen=True)
class StaticScoreMatrices:
    structure_scores_matrix: np.ndarray
    assembly_scores_matrix: np.ndarray
    static_scores_matrix: np.ndarray


@dataclass(frozen=True)
class PreparedScoreData:
    final_scores_matrix: np.ndarray
    structure_scores_matrix: np.ndarray
    assembly_scores_matrix: np.ndarray
    runtime_confidence_by_pair: dict[MatchPairKey, float | None]
    file_descriptor_similarity_by_pair: dict[tuple[str, str], float]
    """Alignment confidence per (non_obf_file_descriptor, obf_file_descriptor) pair."""


@dataclass(frozen=True)
class MatchResult:
    non_obf_signature: MessageAccessSignature
    obf_signature: MessageAccessSignature
    score: float
    group_similarity_score: float
    assembly_similarity_score: float
    structure_similarity_score: float
    field_mapping: dict[str, str]
    field_mapping_infos: FieldMappingInfos
    runtime_confidence: float | None
    match_margin: float
    """Gap between this pair's score and the best competing candidate (row/column)."""
    runner_up_obf: str | None
    """Obfuscated class of the strongest losing alternative for this non-obf target."""
    is_low_confidence: bool
    """Flagged when the score or margin falls under the abstention thresholds."""
    field_mapping_rejected_infos: FieldMappingRejectedInfos
    field_mapping_unmapped_non_obf_fields: FieldMappingUnmappedNonObfFields
    evidence_coverage: float | None
    """Fraction of declared fields backed by runtime access traces (None when none are declared)."""
    is_runtime_observed: bool
    """Whether the obfuscated class was seen in a capture (``evidence_coverage`` is about fields)."""


@dataclass(frozen=True)
class MatchingWorkspace:
    obf_signatures: tuple[MessageAccessSignature, ...]
    non_obf_signatures: tuple[MessageAccessSignature, ...]
    obf_signatures_by_cls: dict[str, MessageAccessSignature]
    non_obf_signatures_by_cls: dict[str, MessageAccessSignature]
    signature_indexes: SignatureIndexLookup
    obf_type_index: dict[str, tuple[DumpCSMessage, ...]]
    non_obf_type_index: dict[str, tuple[DumpCSMessage, ...]]
    obf_groups: dict[str, tuple[MessageAccessSignature, ...]]
    non_obf_groups: dict[str, tuple[MessageAccessSignature, ...]]
    obf_group_root_indexes: dict[str, tuple[int, ...]]
    non_obf_group_root_indexes: dict[str, tuple[int, ...]]
    obf_group_complexity_by_descriptor: dict[str, int]
    non_obf_group_complexity_by_descriptor: dict[str, int]
    obf_field_message_types_by_cls: dict[str, frozenset[str]]
    non_obf_field_message_types_by_cls: dict[str, frozenset[str]]

    @cached_property
    def obf_root_indexes(self) -> frozenset[int]:
        return frozenset(
            index for index, signature in enumerate(self.obf_signatures) if signature.dump_cs_msg.is_root_msg
        )

    @cached_property
    def non_obf_root_indexes(self) -> frozenset[int]:
        return frozenset(
            index
            for index, signature in enumerate(self.non_obf_signatures)
            if signature.dump_cs_msg.is_root_msg
        )

    @cached_property
    def obf_index_items(self) -> tuple[tuple[str, int], ...]:
        return tuple(self.signature_indexes.obf_index_by_cls.items())

    @cached_property
    def non_obf_index_items(self) -> tuple[tuple[str, int], ...]:
        return tuple(self.signature_indexes.non_obf_index_by_cls.items())

    @cached_property
    def obf_group_descriptors(self) -> tuple[str, ...]:
        return tuple(sorted(self.obf_groups))

    @cached_property
    def non_obf_group_descriptors(self) -> tuple[str, ...]:
        return tuple(sorted(self.non_obf_groups))
