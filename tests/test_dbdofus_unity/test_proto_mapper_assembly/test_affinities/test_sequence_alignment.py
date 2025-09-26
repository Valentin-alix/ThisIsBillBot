import numpy as np

from proto_mapper_assembly.affinities._sequence_alignment import align_sequences_monotonically

_GAP_PENALTY = -0.3


def _identity_scores(size: int) -> np.ndarray:
    return np.eye(size)


def test_aligns_identical_sequences_pairwise() -> None:
    aligned = align_sequences_monotonically(
        non_obf_indexes=[0, 1, 2],
        obf_indexes=[0, 1, 2],
        scores_matrix=_identity_scores(3),
        gap_penalty=_GAP_PENALTY,
    )

    assert aligned == ((0, 0), (1, 1), (2, 2))


def test_absorbs_an_insertion_in_the_middle() -> None:
    # The obfuscated build gained one message at position 2: everything after it shifts by one, so a
    # single offset would mismatch the tail. Scores only tie the first and last pairs down.
    scores_matrix = np.zeros((3, 4))
    scores_matrix[0, 0] = 1.0
    scores_matrix[2, 3] = 1.0

    aligned = align_sequences_monotonically(
        non_obf_indexes=[0, 1, 2],
        obf_indexes=[0, 1, 2, 3],
        scores_matrix=scores_matrix,
        gap_penalty=_GAP_PENALTY,
    )

    assert aligned[0] == (0, 0)
    assert aligned[-1] == (2, 3)
    assert [non_obf_index for non_obf_index, _ in aligned] == sorted(
        non_obf_index for non_obf_index, _ in aligned
    )
    assert [obf_index for _, obf_index in aligned] == sorted(obf_index for _, obf_index in aligned)


def test_never_crosses_even_when_scores_reward_it() -> None:
    # A swapped pairing scores higher cell-wise, but crossing is impossible in declaration order.
    scores_matrix = np.array([[0.0, 1.0], [1.0, 0.0]])

    aligned = align_sequences_monotonically(
        non_obf_indexes=[0, 1],
        obf_indexes=[0, 1],
        scores_matrix=scores_matrix,
        gap_penalty=_GAP_PENALTY,
    )

    assert aligned in {((0, 1),), ((1, 0),), ((0, 0), (1, 1))}
    obf_indexes = [obf_index for _, obf_index in aligned]
    assert obf_indexes == sorted(obf_indexes)


def test_returns_nothing_for_an_empty_side() -> None:
    assert (
        align_sequences_monotonically(
            non_obf_indexes=[],
            obf_indexes=[0, 1],
            scores_matrix=_identity_scores(2),
            gap_penalty=_GAP_PENALTY,
        )
        == ()
    )


def test_skips_pairs_that_score_below_the_gap_penalty() -> None:
    # Two zero-score cells cost less as gaps than as a match only when the penalty is small enough;
    # here the middle pair is worth taking, the flanking mismatch is not.
    scores_matrix = np.zeros((2, 2))
    scores_matrix[1, 1] = 1.0

    aligned = align_sequences_monotonically(
        non_obf_indexes=[0, 1],
        obf_indexes=[0, 1],
        scores_matrix=scores_matrix,
        gap_penalty=-0.6,
    )

    assert (1, 1) in aligned
