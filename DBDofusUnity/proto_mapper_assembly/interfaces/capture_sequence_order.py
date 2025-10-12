from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np

from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import CaptureSequencesBySession, RuntimeDataStore

type Cell = tuple[int, int]
"""A (non_obf_index, obf_index) cell of the score matrix."""


@dataclass(frozen=True)
class SequenceMessage:
    """One hinted message that exists in the workspace, with its rank in the hint sequence."""

    position: int
    message_cls: str
    non_obf_index: int


@dataclass(frozen=True)
class Assignment:
    position: int
    obf_index: int


@dataclass(frozen=True)
class BeamState:
    """One reading of a hint sequence: which class each position took, and how well it holds up."""

    assignments: tuple[Assignment, ...]
    used_obf_indexes: frozenset[int]
    objective: float
    order_evidence_count: int
    evidenced_obf_indexes: frozenset[int]
    assigned_obf_indexes: tuple[int, ...] = ()


@dataclass(frozen=True)
class OrderEvidence:
    """What the captures say about one candidate placed against the assignments already made."""

    confidences: tuple[float, ...]
    evidenced_obf_indexes: frozenset[int]


@dataclass(frozen=True)
class CaptureOrderIndex:
    """The capture stream resolved against the workspace, built once for a whole matching run.

    Classes are addressed by matrix index throughout: hints only name root messages and the mask
    keeps root candidates only, so the by-index view covers every pair the beam can build.
    """

    capture_sequences_by_obf_index: Mapping[int, CaptureSequencesBySession]
    captured_obf_indexes: frozenset[int]
    """Observed at all, including the legacy captures that carry no session and no sequence."""
    pinned_obf_indexes: frozenset[int]
    pinned_non_obf_message_classes: frozenset[str]
    confidence_by_obf_pair: dict[Cell, float | None] = field(default_factory=dict[Cell, float | None])

    @classmethod
    def build(
        cls,
        *,
        workspace: MatchingWorkspace,
        pinned_pairs_config: PinnedPairsConfig,
        runtime_data_store: RuntimeDataStore,
    ) -> CaptureOrderIndex:
        # A root obfuscated class carries no namespace, so the runtime key is the class itself.
        # Nested ones do not resolve and are skipped: hints only ever name root messages.
        obf_index_by_cls = workspace.signature_indexes.obf_index_by_cls
        return cls(
            capture_sequences_by_obf_index={
                obf_index: sequences_by_session
                for runtime_key, sequences_by_session in (
                    runtime_data_store.capture_sequences_by_session_by_name.items()
                )
                if (obf_index := obf_index_by_cls.get(runtime_key)) is not None
            },
            captured_obf_indexes=frozenset(
                obf_index
                for runtime_key in runtime_data_store.content_by_name.root
                if (obf_index := obf_index_by_cls.get(runtime_key)) is not None
            ),
            pinned_obf_indexes=frozenset(
                obf_index
                for obf_message_cls in pinned_pairs_config.pinned_pair_msg_by_obf
                if (obf_index := obf_index_by_cls.get(obf_message_cls)) is not None
            ),
            pinned_non_obf_message_classes=frozenset(pinned_pairs_config.pinned_pair_msg_by_non_obf),
        )

    def order_confidence(self, *, before_index: int, after_index: int) -> float | None:
        """Share of capture pairs the client emitted in that order, None without a shared session."""
        pair_key = (before_index, after_index)
        if pair_key in self.confidence_by_obf_pair:
            return self.confidence_by_obf_pair[pair_key]
        before_by_session = self.capture_sequences_by_obf_index.get(before_index, {})
        after_by_session = self.capture_sequences_by_obf_index.get(after_index, {})
        session_scores = [
            _ordered_pair_count(before_sequences, after_sequences)
            / (len(before_sequences) * len(after_sequences))
            # Sorted: summed as floats below, and a set of str iterates differently per process.
            for session_id in sorted(before_by_session.keys() & after_by_session.keys())
            if (before_sequences := before_by_session[session_id])
            and (after_sequences := after_by_session[session_id])
        ]
        confidence = sum(session_scores) / len(session_scores) if session_scores else None
        self.confidence_by_obf_pair[pair_key] = confidence
        return confidence


def _ordered_pair_count(before_sequences: tuple[int, ...], after_sequences: tuple[int, ...]) -> int:
    """How many (before, after) capture pairs are in that order. Both sides must be sorted."""
    at_or_before_count: np.ndarray = np.searchsorted(after_sequences, before_sequences, side="right")
    return len(before_sequences) * len(after_sequences) - int(at_or_before_count.sum())


@dataclass(frozen=True)
class OrderContext:
    workspace: MatchingWorkspace
    scores_matrix: np.ndarray
    capture_order_index: CaptureOrderIndex

    @property
    def capture_sequences_by_obf_index(self) -> Mapping[int, CaptureSequencesBySession]:
        return self.capture_order_index.capture_sequences_by_obf_index

    @property
    def captured_obf_indexes(self) -> frozenset[int]:
        return self.capture_order_index.captured_obf_indexes

    def is_pinned_obf(self, obf_index: int) -> bool:
        return obf_index in self.capture_order_index.pinned_obf_indexes

    def is_pinned_non_obf(self, non_obf_message_cls: str) -> bool:
        return non_obf_message_cls in self.capture_order_index.pinned_non_obf_message_classes

    def scores_row(self, non_obf_index: int) -> list[float]:
        row: list[float] = self.scores_matrix[non_obf_index].tolist()
        return row

    def order_confidence(self, *, before_index: int, after_index: int) -> float | None:
        return self.capture_order_index.order_confidence(before_index=before_index, after_index=after_index)

    def order_evidence(
        self, *, position: int, candidate_index: int, assignments: tuple[Assignment, ...]
    ) -> OrderEvidence:
        confidences: list[float] = []
        evidenced_obf_indexes: set[int] = set()
        for assignment in assignments:
            before_index, after_index = (
                (assignment.obf_index, candidate_index)
                if assignment.position < position
                else (candidate_index, assignment.obf_index)
            )
            confidence = self.order_confidence(before_index=before_index, after_index=after_index)
            if confidence is not None:
                confidences.append(confidence)
                evidenced_obf_indexes.update((before_index, after_index))
        return OrderEvidence(
            confidences=tuple(confidences), evidenced_obf_indexes=frozenset(evidenced_obf_indexes)
        )
