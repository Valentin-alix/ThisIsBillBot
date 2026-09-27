from collections.abc import Sequence
from collections.abc import Set as AbstractSet
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig

_GLOBAL_ASSIGNMENT_BATCH_SIZE = 64


@dataclass(frozen=True)
class SelectedSignaturePair:
    non_obf_signature: MessageAccessSignature
    obf_signature: MessageAccessSignature
    non_obf_index: int
    obf_index: int
    pinned_pair: PinnedPair | None
    score: float
    match_margin: float
    runner_up_obf: str | None


def select_signature_pairs(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
    available_non_obf_indexes: AbstractSet[int],
    available_obf_indexes: AbstractSet[int],
    roots_only: bool,
    pinned_pairs_config: PinnedPairsConfig,
) -> tuple[SelectedSignaturePair, ...]:
    # Preserve workspace order because assignment ties depend on submatrix positions.
    non_obf_rows = sorted(
        available_non_obf_indexes & workspace.non_obf_root_indexes
        if roots_only
        else available_non_obf_indexes
    )
    obf_cols = sorted(
        available_obf_indexes & workspace.obf_root_indexes if roots_only else available_obf_indexes
    )
    if not non_obf_rows or not obf_cols:
        return ()

    row_indices = np.array(non_obf_rows)
    col_indices = np.array(obf_cols)
    submatrix = scores_matrix[np.ix_(row_indices, col_indices)]
    assigned_row_positions, assigned_col_positions = linear_sum_assignment(
        submatrix,
        maximize=True,
    )
    assigned_positions = [
        (int(row_position), int(col_position))
        for row_position, col_position in zip(
            assigned_row_positions,
            assigned_col_positions,
            strict=True,
        )
        if submatrix[row_position, col_position] > 0.0
    ]
    if not assigned_positions:
        return ()

    assignment_margin_by_position = _build_assignment_margin_by_position(
        scores_matrix=submatrix,
        assigned_positions=assigned_positions,
    )
    ranked_positions = sorted(
        assigned_positions,
        key=lambda positions: (
            assignment_margin_by_position[positions],
            float(submatrix[positions]),
            -positions[0],
            -positions[1],
        ),
        reverse=True,
    )
    return tuple(
        _build_selected_signature_pair(
            workspace=workspace,
            submatrix=submatrix,
            row_indices=row_indices,
            col_indices=col_indices,
            row_position=row_position,
            col_position=col_position,
            assignment_margin=assignment_margin_by_position[row_position, col_position],
            pinned_pairs_config=pinned_pairs_config,
        )
        for row_position, col_position in ranked_positions[:_GLOBAL_ASSIGNMENT_BATCH_SIZE]
    )


def _build_selected_signature_pair(
    *,
    workspace: MatchingWorkspace,
    submatrix: np.ndarray,
    row_indices: np.ndarray,
    col_indices: np.ndarray,
    row_position: int,
    col_position: int,
    assignment_margin: float,
    pinned_pairs_config: PinnedPairsConfig,
) -> SelectedSignaturePair:
    best_row_pos = row_position
    best_col_pos = col_position
    best_score = float(submatrix[best_row_pos, best_col_pos])

    non_obf_index = int(row_indices[best_row_pos])
    obf_index = int(col_indices[best_col_pos])
    non_obf_signature = workspace.non_obf_signatures[non_obf_index]
    obf_signature = workspace.obf_signatures[obf_index]

    runner_up_score, runner_up_obf = _resolve_runner_up(
        workspace=workspace,
        submatrix=submatrix,
        col_indices=col_indices,
        best_row_pos=int(best_row_pos),
        best_col_pos=int(best_col_pos),
    )
    match_margin = assignment_margin

    pinned_pair = pinned_pairs_config.pinned_pair_msg_by_obf.get(obf_signature.message_cls)
    if pinned_pair is not None:
        match_margin = best_score - runner_up_score
    return SelectedSignaturePair(
        non_obf_signature=non_obf_signature,
        obf_signature=obf_signature,
        non_obf_index=non_obf_index,
        obf_index=obf_index,
        pinned_pair=pinned_pair,
        score=best_score,
        match_margin=match_margin,
        runner_up_obf=runner_up_obf,
    )


def _build_assignment_margin_by_position(
    *,
    scores_matrix: np.ndarray,
    assigned_positions: Sequence[tuple[int, int]],
) -> dict[tuple[int, int], float]:
    if not assigned_positions:
        return {}

    position_count = len(assigned_positions)
    rows = np.fromiter((row for row, _ in assigned_positions), dtype=np.intp, count=position_count)
    cols = np.fromiter((col for _, col in assigned_positions), dtype=np.intp, count=position_count)
    assigned_scores = scores_matrix[rows, cols]

    best_alternative = np.zeros(position_count, dtype=scores_matrix.dtype)

    free_col_mask = np.ones(int(scores_matrix.shape[1]), dtype=np.bool_)
    free_col_mask[cols] = False
    free_cols = np.flatnonzero(free_col_mask)
    if free_cols.size:
        best_alternative = np.maximum(best_alternative, scores_matrix[np.ix_(rows, free_cols)].max(axis=1))
    free_row_mask = np.ones(int(scores_matrix.shape[0]), dtype=np.bool_)
    free_row_mask[rows] = False
    free_rows = np.flatnonzero(free_row_mask)
    if free_rows.size:
        best_alternative = np.maximum(best_alternative, scores_matrix[np.ix_(free_rows, cols)].max(axis=0))

    # assigned_block and its transpose represent the two halves of a row swap.
    assigned_block = scores_matrix[np.ix_(rows, cols)]
    current_pair_scores = assigned_scores[:, None] + assigned_scores[None, :]
    swapped_pair_scores = assigned_block + assigned_block.T
    swap_alternatives = assigned_scores[:, None] - (current_pair_scores - swapped_pair_scores)
    swap_alternatives[rows[:, None] == rows[None, :]] = -np.inf
    if position_count > 1:
        best_alternative = np.maximum(best_alternative, swap_alternatives.max(axis=1))

    margins = assigned_scores - best_alternative
    return {position: float(margin) for position, margin in zip(assigned_positions, margins, strict=True)}


def _resolve_runner_up(
    *,
    workspace: MatchingWorkspace,
    submatrix: np.ndarray,
    col_indices: np.ndarray,
    best_row_pos: int,
    best_col_pos: int,
) -> tuple[float, str | None]:
    row_scores = submatrix[best_row_pos].copy()
    row_scores[best_col_pos] = -1.0
    best_alt_col_pos = int(np.argmax(row_scores))
    best_row_alternative = float(row_scores[best_alt_col_pos])

    column_scores = submatrix[:, best_col_pos].copy()
    column_scores[best_row_pos] = -1.0
    best_column_alternative = float(column_scores.max())

    runner_up_score = max(best_row_alternative, best_column_alternative, 0.0)
    runner_up_obf = (
        workspace.obf_signatures[int(col_indices[best_alt_col_pos])].message_cls
        if best_row_alternative > 0.0
        else None
    )
    return runner_up_score, runner_up_obf
