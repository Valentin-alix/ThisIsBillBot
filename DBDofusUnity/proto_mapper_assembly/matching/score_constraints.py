from __future__ import annotations

import numpy as np

from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from proto_mapper_assembly.matching.capture_sequence_order import apply_capture_sequence_order_scores
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore

_STORE_MATCH_BONUS = 0.1
_PARENT_CANDIDATE_THRESHOLD = 0.3


def build_adjusted_scores_matrix(
    *,
    workspace: MatchingWorkspace,
    base_scores_matrix: np.ndarray,
    matching_store: IterativeMatchingStore,
    capture_order_index: CaptureOrderIndex,
    capture_sequence_hints_config: CaptureSequenceHintsConfig,
) -> np.ndarray:
    """Adjust matrix score based on already matched messages."""
    adjusted_scores_matrix = np.array(base_scores_matrix, copy=True)
    indexed_view = matching_store.get_indexed_view(workspace)
    expected_obf = indexed_view.expected_obf_indexes
    expected_non_obf = indexed_view.expected_non_obf_indexes

    # An expected pair keeps its column to itself, and the columns are disjoint.
    expected_scores = base_scores_matrix[expected_non_obf, expected_obf]
    expected_scores = np.where(expected_scores <= 0.0, indexed_view.expected_inferred_scores, expected_scores)
    adjusted_scores_matrix[:, expected_obf] = 0.0
    adjusted_scores_matrix[expected_non_obf, expected_obf] = expected_scores

    # Same for a confirmed pair and its row, read before any row is cleared.
    confirmed_obf = indexed_view.confirmed_obf_indexes
    confirmed_non_obf = indexed_view.confirmed_non_obf_indexes
    allowed_scores = adjusted_scores_matrix[confirmed_non_obf, confirmed_obf].copy()
    adjusted_scores_matrix[confirmed_non_obf, :] = 0.0
    adjusted_scores_matrix[confirmed_non_obf, confirmed_obf] = allowed_scores

    bonus_scores = adjusted_scores_matrix[expected_non_obf, expected_obf]
    has_bonus = bonus_scores > 0.0
    adjusted_scores_matrix[expected_non_obf[has_bonus], expected_obf[has_bonus]] = np.minimum(
        1.0, bonus_scores[has_bonus] + _STORE_MATCH_BONUS
    )
    apply_capture_sequence_order_scores(
        workspace=workspace,
        scores_matrix=adjusted_scores_matrix,
        matching_store=matching_store,
        capture_order_index=capture_order_index,
        capture_sequence_hints_config=capture_sequence_hints_config,
    )
    return adjusted_scores_matrix


def build_prospective_constraint_mask(
    *,
    workspace: MatchingWorkspace,
    base_scores_matrix: np.ndarray,
) -> np.ndarray:
    """
    Precompute a global message-level mask from parent/child compatibility.

    The mask zeros obf-child -> non-obf-X when X is not a field message type
    of any strong non-obfuscated candidate for the child's obfuscated parent.
    """
    mask = np.ones_like(base_scores_matrix)
    valid_for_child: dict[str, set[str]] = {}

    for obf_parent_cls, obf_children in workspace.obf_field_message_types_by_cls.items():
        obf_parent_idx = workspace.signature_indexes.obf_index_by_cls[obf_parent_cls]
        valid: set[str] = set()
        for non_obf_idx, non_obf_sig in enumerate(workspace.non_obf_signatures):
            if base_scores_matrix[non_obf_idx, obf_parent_idx] > _PARENT_CANDIDATE_THRESHOLD:
                valid.update(
                    workspace.non_obf_field_message_types_by_cls.get(non_obf_sig.message_cls, frozenset())
                )
        for obf_child_cls in obf_children:
            valid_for_child.setdefault(obf_child_cls, set()).update(valid)

    for obf_child_cls, valid_non_obf in valid_for_child.items():
        obf_child_idx = workspace.signature_indexes.obf_index_by_cls[obf_child_cls]
        for non_obf_idx, non_obf_sig in enumerate(workspace.non_obf_signatures):
            if non_obf_sig.message_cls not in valid_non_obf:
                mask[non_obf_idx, obf_child_idx] = 0.0

    return mask
