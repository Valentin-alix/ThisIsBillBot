from collections import Counter

import numpy as np
import pytest

from DBDofusUnity.proto_mapper_assembly.scoring.primitives import (
    counter_overlap_similarity,
    get_average_best_similarity_sequences,
    ratio_similarity,
)

type SizeCase = tuple[int, int, float]
type ForeignAccessCase = tuple[Counter[str], Counter[str], float]
type SequenceCase = tuple[list[int], list[int], float]
_SIZE_CASES: list[SizeCase] = [
    (100, 100, 1.0),
    (100, 200, 0.5),
]


_FOREIGN_ACCESS_CASES: list[ForeignAccessCase] = [
    (Counter(), Counter(), 1.0),
    (
        Counter({"field:read": 2, "field:write": 1}),
        Counter({"field:read": 2, "field:write": 1}),
        1.0,
    ),
    (Counter({"a:read": 2}), Counter({"b:read": 3}), 0.0),
    (Counter({"a": 1, "b": 1}), Counter({"a": 1, "c": 1}), 0.5),
    (Counter({"a": 1}), Counter(), 0.0),
]


_SEQUENCE_CASES: list[SequenceCase] = [
    ([], [], 1.0),
    ([], [1], 0.0),
    ([1], [], 0.0),
    ([1, 2, 3], [1, 2, 3], 1.0),
    ([1], [1, 2], np.float64(0.5)),
    ([1, 2], [3, 4], 0.0),
]


def _exact_match_similarity(left_item: int, right_item: int) -> float:
    return 1.0 if left_item == right_item else 0.0


class TestScoringPrimitives:
    @pytest.mark.parametrize(("left", "right", "expected"), _SIZE_CASES)
    def test_size_similarity_distinguishes_equal_and_different_sizes(
        self,
        left: int,
        right: int,
        expected: float,
    ) -> None:
        assert ratio_similarity(left, right, max_value=max(left, right)) == expected

    def test_size_similarity_is_symmetric(self) -> None:
        assert ratio_similarity(80, 100, max_value=100) == ratio_similarity(100, 80, max_value=100)

    @pytest.mark.parametrize(("left_counter", "right_counter", "expected"), _FOREIGN_ACCESS_CASES)
    def test_foreign_access_overlap_similarity_handles_empty_identical_partial_and_disjoint_counters(
        self, left_counter: Counter[str], right_counter: Counter[str], expected: float
    ) -> None:
        result = counter_overlap_similarity(left_counter=left_counter, right_counter=right_counter)

        assert result == pytest.approx(expected)  # pyright: ignore[reportUnknownMemberType]

    @pytest.mark.parametrize(("left", "right", "expected"), _SEQUENCE_CASES)
    def test_get_average_best_similarity_sequences_handles_empty_identical_length_mismatch_and_disjoint_sequences(
        self,
        left: list[int],
        right: list[int],
        expected: float,
    ) -> None:
        result = get_average_best_similarity_sequences(left, right, _exact_match_similarity)

        assert result == expected
