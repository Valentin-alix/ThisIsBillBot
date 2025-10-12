from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from dataclasses import field as dataclass_field
from itertools import chain

import numpy as np
from base_python.cache import cache

from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import DiscoveredMessageMatch
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey


@dataclass(frozen=True)
class IndexedMatchingStoreView:
    """The store as matrix coordinates: only the pairs it holds, never one entry per message."""

    expected_obf_indexes: np.ndarray
    expected_non_obf_indexes: np.ndarray
    """Target of each obfuscated message, confirmed or inferred; also the bonus target."""
    expected_inferred_scores: np.ndarray
    """Fallback for an expected pair the base matrix scores at zero."""
    confirmed_obf_indexes: np.ndarray
    confirmed_non_obf_indexes: np.ndarray


@cache
def build_indexed_matching_store_view(
    *,
    confirmed_non_obf_items: tuple[MatchPairKey, ...],
    confirmed_obf_items: tuple[MatchPairKey, ...],
    inferred_non_obf_items: tuple[MatchPairKey, ...],
    inferred_score_items: tuple[tuple[MatchPairKey, float], ...],
    obf_index_items: tuple[tuple[str, int], ...],
    non_obf_index_items: tuple[tuple[str, int], ...],
) -> IndexedMatchingStoreView:
    obf_index_by_cls = dict(obf_index_items)
    non_obf_index_by_cls = dict(non_obf_index_items)
    inferred_score_by_pair = dict(inferred_score_items)

    # Confirmed pairs come last so they overwrite the inferred expectation for the same class.
    expected_by_obf_index: dict[int, tuple[int, float]] = {}
    for obf_message_cls, non_obf_message_cls in chain(inferred_non_obf_items, confirmed_non_obf_items):
        obf_index = obf_index_by_cls.get(obf_message_cls)
        non_obf_index = non_obf_index_by_cls.get(non_obf_message_cls)
        if obf_index is None or non_obf_index is None:
            continue
        expected_by_obf_index[obf_index] = (
            non_obf_index,
            inferred_score_by_pair.get(MatchPairKey(obf_message_cls, non_obf_message_cls), 0),
        )

    confirmed_obf_index_by_non_obf_index: dict[int, int] = {}
    for obf_message_cls, non_obf_message_cls in confirmed_obf_items:
        non_obf_index = non_obf_index_by_cls.get(non_obf_message_cls)
        obf_index = obf_index_by_cls.get(obf_message_cls)
        if non_obf_index is None or obf_index is None:
            continue
        confirmed_obf_index_by_non_obf_index[non_obf_index] = obf_index

    return IndexedMatchingStoreView(
        expected_obf_indexes=_index_array(expected_by_obf_index.keys()),
        expected_non_obf_indexes=_index_array(
            non_obf_index for non_obf_index, _ in expected_by_obf_index.values()
        ),
        expected_inferred_scores=np.fromiter(
            (inferred_score for _, inferred_score in expected_by_obf_index.values()),
            dtype=np.float64,
            count=len(expected_by_obf_index),
        ),
        confirmed_obf_indexes=_index_array(confirmed_obf_index_by_non_obf_index.values()),
        confirmed_non_obf_indexes=_index_array(confirmed_obf_index_by_non_obf_index.keys()),
    )


def _index_array(indexes: Iterable[int]) -> np.ndarray:
    return np.fromiter(indexes, dtype=np.intp)


@dataclass
class IterativeMatchingStore:
    confirmed_non_obf_by_obf: dict[str, str] = dataclass_field(default_factory=dict[str, str])
    confirmed_obf_by_non_obf: dict[str, str] = dataclass_field(default_factory=dict[str, str])
    inferred_non_obf_by_obf: dict[str, str] = dataclass_field(default_factory=dict[str, str])
    inferred_confidence_by_pair: dict[MatchPairKey, float] = dataclass_field(
        default_factory=dict[MatchPairKey, float]
    )
    source_by_obf: dict[str, str] = dataclass_field(default_factory=dict[str, str])
    version: int = 0

    def get_indexed_view(self, workspace: MatchingWorkspace) -> IndexedMatchingStoreView:
        return build_indexed_matching_store_view(
            confirmed_non_obf_items=tuple(
                MatchPairKey(obf_message_cls, non_obf_message_cls)
                for obf_message_cls, non_obf_message_cls in self.confirmed_non_obf_by_obf.items()
            ),
            confirmed_obf_items=tuple(
                MatchPairKey(obf_message_cls, non_obf_message_cls)
                for non_obf_message_cls, obf_message_cls in self.confirmed_obf_by_non_obf.items()
            ),
            inferred_non_obf_items=tuple(
                MatchPairKey(obf_message_cls, non_obf_message_cls)
                for obf_message_cls, non_obf_message_cls in self.inferred_non_obf_by_obf.items()
            ),
            inferred_score_items=tuple(self.inferred_confidence_by_pair.items()),
            obf_index_items=workspace.obf_index_items,
            non_obf_index_items=workspace.non_obf_index_items,
        )

    def get_expected_non_obf(self, obf_message_cls: str) -> str | None:
        confirmed = self.confirmed_non_obf_by_obf.get(obf_message_cls)
        if confirmed is not None:
            return confirmed
        return self.inferred_non_obf_by_obf.get(obf_message_cls)

    def supports_pair(self, obf_message_cls: str, non_obf_message_cls: str) -> bool:
        """Check if matching pair match with already matched pair in store."""
        return self.get_expected_non_obf(obf_message_cls) == non_obf_message_cls

    def conflicts_with_pair(self, obf_message_cls: str, non_obf_message_cls: str) -> bool:
        """Check if matching pair will conflict with already matched pair in store."""
        confirmed_non_obf = self.confirmed_non_obf_by_obf.get(obf_message_cls)
        if confirmed_non_obf is not None and confirmed_non_obf != non_obf_message_cls:
            return True

        confirmed_obf = self.confirmed_obf_by_non_obf.get(non_obf_message_cls)
        if confirmed_obf is not None and confirmed_obf != obf_message_cls:
            return True

        inferred_non_obf = self.inferred_non_obf_by_obf.get(obf_message_cls)
        return inferred_non_obf is not None and inferred_non_obf != non_obf_message_cls

    def register_confirmed(
        self,
        *,
        obf_message_cls: str,
        non_obf_message_cls: str,
        source: str,
    ) -> bool:
        if self.conflicts_with_pair(obf_message_cls, non_obf_message_cls):
            return False
        self.confirmed_non_obf_by_obf[obf_message_cls] = non_obf_message_cls
        self.confirmed_obf_by_non_obf[non_obf_message_cls] = obf_message_cls
        self.source_by_obf[obf_message_cls] = source
        self.version += 1
        return True

    def register_inferred(self, discovery: DiscoveredMessageMatch) -> bool:
        if self.conflicts_with_pair(discovery.obf_message_cls, discovery.non_obf_message_cls):
            return False
        previous_length = len(self.inferred_non_obf_by_obf)
        self.inferred_non_obf_by_obf.setdefault(
            discovery.obf_message_cls,
            discovery.non_obf_message_cls,
        )
        self.inferred_confidence_by_pair.setdefault(
            MatchPairKey(discovery.obf_message_cls, discovery.non_obf_message_cls),
            discovery.confidence,
        )
        self.source_by_obf.setdefault(discovery.obf_message_cls, discovery.reason)
        if len(self.inferred_non_obf_by_obf) != previous_length:
            self.version += 1
        return True
