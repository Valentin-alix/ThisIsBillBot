from collections.abc import Sequence

import numpy as np

_MATCH = 0
_SKIP_LEFT = 1
_SKIP_RIGHT = 2


def align_sequences_monotonically(
    *,
    non_obf_indexes: Sequence[int],
    obf_indexes: Sequence[int],
    scores_matrix: np.ndarray,
    gap_penalty: float,
) -> tuple[tuple[int, int], ...]:
    """Align matrix indexes without crossing; gaps absorb inserted or removed messages."""
    left_count = len(non_obf_indexes)
    right_count = len(obf_indexes)
    if left_count == 0 or right_count == 0:
        return ()

    best_scores = np.zeros((left_count + 1, right_count + 1))
    moves = np.zeros((left_count + 1, right_count + 1), dtype=np.int8)
    best_scores[1:, 0] = np.arange(1, left_count + 1) * gap_penalty
    moves[1:, 0] = _SKIP_LEFT
    best_scores[0, 1:] = np.arange(1, right_count + 1) * gap_penalty
    moves[0, 1:] = _SKIP_RIGHT

    for left_position in range(1, left_count + 1):
        non_obf_index = non_obf_indexes[left_position - 1]
        for right_position in range(1, right_count + 1):
            obf_index = obf_indexes[right_position - 1]
            match_score = best_scores[left_position - 1, right_position - 1] + float(
                scores_matrix[non_obf_index, obf_index]
            )
            skip_left_score = best_scores[left_position - 1, right_position] + gap_penalty
            skip_right_score = best_scores[left_position, right_position - 1] + gap_penalty
            if match_score >= skip_left_score and match_score >= skip_right_score:
                best_scores[left_position, right_position] = match_score
                moves[left_position, right_position] = _MATCH
            elif skip_left_score >= skip_right_score:
                best_scores[left_position, right_position] = skip_left_score
                moves[left_position, right_position] = _SKIP_LEFT
            else:
                best_scores[left_position, right_position] = skip_right_score
                moves[left_position, right_position] = _SKIP_RIGHT

    aligned_pairs: list[tuple[int, int]] = []
    left_position, right_position = left_count, right_count
    while left_position > 0 and right_position > 0:
        move = moves[left_position, right_position]
        if move == _MATCH:
            aligned_pairs.append((non_obf_indexes[left_position - 1], obf_indexes[right_position - 1]))
            left_position -= 1
            right_position -= 1
        elif move == _SKIP_LEFT:
            left_position -= 1
        else:
            right_position -= 1
    return tuple(reversed(aligned_pairs))
