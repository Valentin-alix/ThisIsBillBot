from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pytest

from DBDofusUnity.proto_mapper_assembly.matching.pair_selection import _build_assignment_margin_by_position


def _scalar_assignment_margin_by_position(
    *,
    scores_matrix: np.ndarray,
    assigned_positions: Sequence[tuple[int, int]],
) -> dict[tuple[int, int], float]:
    """The pre-vectorisation implementation, kept as the equivalence oracle."""
    assigned_rows = {row_position for row_position, _ in assigned_positions}
    assigned_cols = {col_position for _, col_position in assigned_positions}
    unassigned_rows = set(range(scores_matrix.shape[0])) - assigned_rows
    unassigned_cols = set(range(scores_matrix.shape[1])) - assigned_cols

    margin_by_position: dict[tuple[int, int], float] = {}
    for row_position, col_position in assigned_positions:
        assigned_score = float(scores_matrix[row_position, col_position])
        alternative_scores = [0.0]
        alternative_scores.extend(
            float(scores_matrix[row_position, alternative_col]) for alternative_col in unassigned_cols
        )
        alternative_scores.extend(
            float(scores_matrix[alternative_row, col_position]) for alternative_row in unassigned_rows
        )
        for other_row, other_col in assigned_positions:
            if other_row == row_position:
                continue
            current_pair_score = assigned_score + float(scores_matrix[other_row, other_col])
            swapped_pair_score = float(
                scores_matrix[row_position, other_col] + scores_matrix[other_row, col_position]
            )
            alternative_scores.append(assigned_score - (current_pair_score - swapped_pair_score))
        margin_by_position[row_position, col_position] = assigned_score - max(alternative_scores)
    return margin_by_position


def _build_random_case(
    *, row_count: int, col_count: int, assigned_count: int, seed: int
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    generator = np.random.default_rng(seed)
    scores_matrix = generator.random((row_count, col_count))
    rows = generator.permutation(row_count)[:assigned_count]
    cols = generator.permutation(col_count)[:assigned_count]
    return scores_matrix, [(int(row), int(col)) for row, col in zip(rows, cols, strict=True)]


class TestBuildAssignmentMarginByPosition:
    @pytest.mark.parametrize(
        ("row_count", "col_count", "assigned_count"),
        [
            (1, 1, 1),
            (1, 4, 1),
            (4, 1, 1),
            (3, 3, 3),
            (5, 8, 5),
            (8, 5, 5),
            (12, 12, 7),
            (30, 24, 24),
        ],
    )
    def test_matches_the_scalar_implementation(
        self, row_count: int, col_count: int, assigned_count: int
    ) -> None:
        for seed in range(5):
            scores_matrix, assigned_positions = _build_random_case(
                row_count=row_count,
                col_count=col_count,
                assigned_count=assigned_count,
                seed=seed,
            )
            expected = _scalar_assignment_margin_by_position(
                scores_matrix=scores_matrix, assigned_positions=assigned_positions
            )
            actual = _build_assignment_margin_by_position(
                scores_matrix=scores_matrix, assigned_positions=assigned_positions
            )
            assert actual.keys() == expected.keys()
            for position, expected_margin in expected.items():
                assert actual[position] == pytest.approx(expected_margin, abs=0.0, rel=0.0)

    def test_returns_nothing_without_assigned_positions(self) -> None:
        assert (
            _build_assignment_margin_by_position(scores_matrix=np.zeros((3, 3)), assigned_positions=[]) == {}
        )

    def test_margin_is_never_positive_against_a_stronger_free_column(self) -> None:
        # Row 0 is assigned to column 0 while the free column 1 scores higher on the same row.
        scores_matrix = np.array([[0.4, 0.9]])
        margins = _build_assignment_margin_by_position(
            scores_matrix=scores_matrix, assigned_positions=[(0, 0)]
        )
        assert margins[0, 0] == pytest.approx(0.4 - 0.9)
