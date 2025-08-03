from __future__ import annotations

from collections.abc import Callable, Mapping
from functools import cache

import numpy as np

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.scoring.message_scoring import (
    MessageSimilarityScoreData,
    StructureSimilarityContext,
    compute_message_similarity,
    compute_structure_score,
)


class LazyScoreByPair(dict[MatchPairKey, float]):
    def __init__(self, resolver: Callable[[str, str], float]) -> None:
        super().__init__()
        self._resolver = resolver

    def __missing__(self, key: MatchPairKey) -> float:
        obf_cls, non_obf_cls = key
        value = self._resolver(obf_cls, non_obf_cls)
        self[key] = value
        return value


def build_lazy_score_by_pair_lookup_from_matrix(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
) -> LazyScoreByPair:
    @cache
    def resolve_score(obf_cls: str, non_obf_cls: str) -> float:
        obf_index = workspace.signature_indexes.obf_index_by_cls.get(obf_cls)
        non_obf_index = workspace.signature_indexes.non_obf_index_by_cls.get(non_obf_cls)
        if obf_index is None or non_obf_index is None:
            error = MatchPairKey(obf_cls, non_obf_cls)
            raise KeyError(error)
        return float(scores_matrix[non_obf_index, obf_index])

    return LazyScoreByPair(resolve_score)


def build_lazy_score_by_pair_lookup_from_signatures(
    *,
    obf_signatures_by_cls: Mapping[str, MessageAccessSignature],
    non_obf_signatures_by_cls: Mapping[str, MessageAccessSignature],
    structure_context: StructureSimilarityContext,
) -> LazyScoreByPair:
    @cache
    def resolve_score(obf_cls: str, non_obf_cls: str) -> float:
        try:
            obf_signature = obf_signatures_by_cls[obf_cls]
            non_obf_signature = non_obf_signatures_by_cls[non_obf_cls]
        except KeyError as error:
            raise KeyError(MatchPairKey(obf_cls, non_obf_cls)) from error
        return build_message_pair_static_score(
            obf_signature,
            non_obf_signature,
            structure_context=structure_context,
        ).static_similarity

    return LazyScoreByPair(resolve_score)


def build_message_pair_static_score(
    left: MessageAccessSignature,
    right: MessageAccessSignature,
    *,
    structure_context: StructureSimilarityContext,
) -> MessageSimilarityScoreData:
    """Return the static score breakdown for a single message pair."""
    structure_score = compute_structure_score(left, right, context=structure_context)
    return compute_message_similarity(left, right, structure_score=structure_score)
