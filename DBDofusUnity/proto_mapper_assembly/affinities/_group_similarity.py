from collections.abc import Sequence

import numpy as np
from scipy.optimize import linear_sum_assignment


def build_group_scores_matrix(
    *,
    base_scores_matrix: np.ndarray,
    non_obf_groups: Sequence[Sequence[int]],
    obf_groups: Sequence[Sequence[int]],
) -> np.ndarray:
    group_scores_matrix = np.zeros((len(non_obf_groups), len(obf_groups)))
    for non_obf_group_index, non_obf_members in enumerate(non_obf_groups):
        for obf_group_index, obf_members in enumerate(obf_groups):
            submatrix = base_scores_matrix[np.ix_(non_obf_members, obf_members)]
            group_scores_matrix[non_obf_group_index, obf_group_index] = get_group_similarity_score(
                similarity_matrix=submatrix,
                non_obf_count=len(non_obf_members),
                obf_count=len(obf_members),
            )
    return group_scores_matrix


def match_groups(
    *,
    group_scores_matrix: np.ndarray,
    min_score: float,
    min_margin: float,
) -> tuple[tuple[int, int], ...]:
    """Return confident (non_obf_group_index, obf_group_index) pairs; thresholds depend on the grouping."""
    matched_groups: list[tuple[int, int]] = []
    non_obf_indexes, obf_indexes = linear_sum_assignment(group_scores_matrix, maximize=True)
    for non_obf_index_value, obf_index_value in zip(non_obf_indexes, obf_indexes, strict=True):
        non_obf_group_index = int(non_obf_index_value)
        obf_group_index = int(obf_index_value)
        assigned_score = float(group_scores_matrix[non_obf_group_index, obf_group_index])
        if assigned_score <= min_score:
            continue
        runner_up_score = max(
            _best_competing_score(group_scores_matrix[non_obf_group_index, :], obf_group_index),
            _best_competing_score(group_scores_matrix[:, obf_group_index], non_obf_group_index),
        )
        if assigned_score - runner_up_score < min_margin:
            continue
        matched_groups.append((non_obf_group_index, obf_group_index))
    return tuple(matched_groups)


def _best_competing_score(scores: np.ndarray, assigned_index: int) -> float:
    competing_scores = np.delete(scores, assigned_index)
    if competing_scores.size == 0:
        return 0.0
    return float(competing_scores.max())


def get_group_similarity_score(
    similarity_matrix: np.ndarray,
    non_obf_count: int,
    obf_count: int,
) -> float:
    if similarity_matrix.size == 0:
        return 0.0

    non_obf_indexes, obf_indexes = linear_sum_assignment(similarity_matrix, maximize=True)
    total_score = 0.0
    for non_obf_index, obf_index in zip(non_obf_indexes, obf_indexes, strict=True):
        total_score += float(similarity_matrix[non_obf_index, obf_index])
    assigned_count = min(non_obf_count, obf_count)
    max_group_count = max(non_obf_count, obf_count)
    if assigned_count == 0 or max_group_count == 0:
        return 0.0

    normalization_count = assigned_count if non_obf_count == obf_count else max_group_count
    return total_score / normalization_count
