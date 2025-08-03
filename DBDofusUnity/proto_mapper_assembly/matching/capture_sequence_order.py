from __future__ import annotations

from bisect import bisect_left, bisect_right
from collections import defaultdict
from collections.abc import Mapping
from math import exp, log

import numpy as np

from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.capture_sequence_order import (
    Assignment,
    BeamState,
    CaptureOrderIndex,
    Cell,
    OrderContext,
    SequenceMessage,
)
from proto_mapper_assembly.interfaces.matching import MatchingWorkspace
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore

_CANDIDATE_LIMIT = 5
_CAPTURED_CANDIDATE_LIMIT = 10
_WINDOW_CANDIDATE_LIMIT = 10
_BEAM_WIDTH = 128
_MIN_SEQUENCE_MESSAGE_COUNT = 2
_SUPPORT_TEMPERATURE = 4.0
_MIN_MULTIPLIER = 0.90
_MULTIPLIER_SPREAD = 0.25
_MAX_COMPETITOR_PENALTY = 0.75


def apply_capture_sequence_order_scores(
    *,
    workspace: MatchingWorkspace,
    scores_matrix: np.ndarray,
    matching_store: IterativeMatchingStore,
    capture_order_index: CaptureOrderIndex,
    capture_sequence_hints_config: CaptureSequenceHintsConfig,
) -> None:
    """Reshape the scores with what the captures say about the order messages are emitted in."""
    context = OrderContext(
        workspace=workspace,
        scores_matrix=scores_matrix,
        capture_order_index=capture_order_index,
    )
    supports_by_cell: dict[Cell, list[float]] = defaultdict(list)
    non_obf_indexes_by_window_obf_index: defaultdict[int, set[int]] = defaultdict(set)
    for sequence in capture_sequence_hints_config.sequences:
        messages = tuple(
            SequenceMessage(position=position, message_cls=message_cls, non_obf_index=non_obf_index)
            for position, message_cls in enumerate(sequence.messages)
            if (non_obf_index := workspace.signature_indexes.non_obf_index_by_cls.get(message_cls))
            is not None
        )
        window_candidates_by_position = _build_window_candidates_by_position(
            context=context, messages=messages, matching_store=matching_store
        )
        for message in messages:
            # A window holding exactly one class identifies it, as long as neither side is pinned.
            window_candidate_indexes = window_candidates_by_position.get(message.position, ())
            if (
                len(window_candidate_indexes) == 1
                and not context.is_pinned_non_obf(message.message_cls)
                and not context.is_pinned_obf(window_candidate_indexes[0])
            ):
                non_obf_indexes_by_window_obf_index[window_candidate_indexes[0]].add(message.non_obf_index)
        for cell, support in _sequence_supports_by_cell(
            context=context,
            messages=messages,
            matching_store=matching_store,
            window_candidates_by_position=window_candidates_by_position,
        ).items():
            supports_by_cell[cell].append(support)

    _apply_support_to_scores(context=context, supports_by_cell=supports_by_cell)
    _apply_sole_window_candidates(
        context=context, non_obf_indexes_by_window_obf_index=non_obf_indexes_by_window_obf_index
    )


def _sequence_supports_by_cell(
    *,
    context: OrderContext,
    messages: tuple[SequenceMessage, ...],
    matching_store: IterativeMatchingStore,
    window_candidates_by_position: Mapping[int, tuple[int, ...]],
) -> dict[Cell, float]:
    """How strongly one hint sequence backs each pair, weighing states by distance to the best one."""
    message_candidates = tuple(
        (message, candidate_indexes)
        for message in messages
        if (
            candidate_indexes := _get_candidate_indexes(
                context=context,
                message=message,
                matching_store=matching_store,
                window_candidate_indexes=window_candidates_by_position.get(message.position, ()),
            )
        )
    )
    if len(message_candidates) < _MIN_SEQUENCE_MESSAGE_COUNT:
        return {}
    states = tuple(
        state
        for state in _build_sequence_beam(context=context, message_candidates=message_candidates)
        if state.order_evidence_count > 0
    )
    if not states:
        return {}
    non_obf_index_by_position = {message.position: message.non_obf_index for message, _ in message_candidates}
    best_objective = max(state.objective for state in states)
    supports_by_cell: dict[Cell, float] = {}
    for state in states:
        support = exp(min(0.0, (state.objective - best_objective) * _SUPPORT_TEMPERATURE))
        for assignment in state.assignments:
            if assignment.obf_index not in state.evidenced_obf_indexes:
                continue
            cell = (non_obf_index_by_position[assignment.position], assignment.obf_index)
            supports_by_cell[cell] = max(supports_by_cell.get(cell, 0.0), support)
    return supports_by_cell


def _build_sequence_beam(
    *,
    context: OrderContext,
    message_candidates: tuple[tuple[SequenceMessage, tuple[int, ...]], ...],
) -> tuple[BeamState, ...]:
    """Best complete readings of one sequence, scored on cell strength times order consistency."""
    beam = (
        BeamState(
            assignments=(),
            used_obf_indexes=frozenset(),
            objective=0.0,
            order_evidence_count=0,
            evidenced_obf_indexes=frozenset(),
        ),
    )
    for message, candidate_indexes in message_candidates:
        scores_row = context.scores_row(message.non_obf_index)
        log_score_by_candidate: dict[int, float] = {}
        for candidate_index in candidate_indexes:
            candidate_score = scores_row[candidate_index]
            assert candidate_score > 0.0
            log_score_by_candidate[candidate_index] = log(candidate_score)

        expanded_states: list[BeamState] = []
        for state in beam:
            for candidate_index in candidate_indexes:
                if candidate_index in state.used_obf_indexes:
                    continue
                evidence = context.order_evidence(
                    position=message.position,
                    candidate_index=candidate_index,
                    assignments=state.assignments,
                )
                order_multiplier = 1.0
                if evidence.confidences:
                    confidence = sum(evidence.confidences) / len(evidence.confidences)
                    order_multiplier = _MIN_MULTIPLIER + confidence * _MULTIPLIER_SPREAD
                expanded_states.append(
                    BeamState(
                        assignments=(
                            *state.assignments,
                            Assignment(position=message.position, obf_index=candidate_index),
                        ),
                        used_obf_indexes=state.used_obf_indexes | {candidate_index},
                        objective=(
                            state.objective + log_score_by_candidate[candidate_index] + log(order_multiplier)
                        ),
                        order_evidence_count=state.order_evidence_count + len(evidence.confidences),
                        evidenced_obf_indexes=state.evidenced_obf_indexes | evidence.evidenced_obf_indexes,
                        assigned_obf_indexes=(*state.assigned_obf_indexes, candidate_index),
                    )
                )
        if not expanded_states:
            return ()
        expanded_states.sort(key=lambda state: (-state.objective, state.assigned_obf_indexes))
        beam = tuple(expanded_states[:_BEAM_WIDTH])
    return beam


def _get_candidate_indexes(
    *,
    context: OrderContext,
    message: SequenceMessage,
    matching_store: IterativeMatchingStore,
    window_candidate_indexes: tuple[int, ...],
) -> tuple[int, ...]:
    """The classes worth trying for one hinted message: best scoring, then observed, then in-window."""
    confirmed_obf_cls = matching_store.confirmed_obf_by_non_obf.get(message.message_cls)
    if confirmed_obf_cls is not None:
        return (context.workspace.signature_indexes.obf_index_by_cls[confirmed_obf_cls],)
    scores_row = context.scores_row(message.non_obf_index)
    ranked_indexes = sorted(
        (int(index) for index in np.flatnonzero(context.scores_matrix[message.non_obf_index] > 0.0)),
        key=lambda candidate_index: scores_row[candidate_index],
        reverse=True,
    )
    captured_indexes = [
        candidate_index
        for candidate_index in ranked_indexes
        if candidate_index in context.captured_obf_indexes
    ]
    return tuple(
        dict.fromkeys(
            (
                *ranked_indexes[:_CANDIDATE_LIMIT],
                *captured_indexes[:_CAPTURED_CANDIDATE_LIMIT],
                *window_candidate_indexes,
            )
        )
    )


def _build_window_candidates_by_position(
    *,
    context: OrderContext,
    messages: tuple[SequenceMessage, ...],
    matching_store: IterativeMatchingStore,
) -> dict[int, tuple[int, ...]]:
    """Observed classes captured between each open position's settled neighbours, whatever they score.

    A class moved out of its package never survives a score shortlist, but where it sits in the
    capture stream does not care where it was declared - hence this third lane.
    """
    obf_index_by_cls = context.workspace.signature_indexes.obf_index_by_cls
    anchor_obf_index_by_position = {
        message.position: obf_index_by_cls[confirmed_obf_cls]
        for message in messages
        if (confirmed_obf_cls := matching_store.confirmed_obf_by_non_obf.get(message.message_cls)) is not None
        and confirmed_obf_cls in obf_index_by_cls
    }
    candidates_by_position: dict[int, tuple[int, ...]] = {}
    for message in messages:
        # A settled message keeps its confirmed class, so its own window would be read by nobody.
        if message.position in anchor_obf_index_by_position:
            continue
        bounds_by_session = _window_bounds_by_session(
            context=context,
            position=message.position,
            anchor_obf_index_by_position=anchor_obf_index_by_position,
        )
        if not bounds_by_session:
            continue
        scores_row = context.scores_row(message.non_obf_index)
        window_indexes = [
            obf_index
            for obf_index, sequences_by_session in context.capture_sequences_by_obf_index.items()
            if scores_row[obf_index] > 0.0
            and any(
                _has_sequence_strictly_between(
                    sequences_by_session.get(session_id, ()), lower=lower, upper=upper
                )
                for session_id, (lower, upper) in bounds_by_session.items()
            )
        ]
        window_indexes.sort(key=lambda obf_index: scores_row[obf_index], reverse=True)
        candidates_by_position[message.position] = tuple(window_indexes[:_WINDOW_CANDIDATE_LIMIT])
    return candidates_by_position


def _has_sequence_strictly_between(capture_sequences: tuple[int, ...], *, lower: int, upper: int) -> bool:
    """Whether any capture sits strictly inside the window. ``capture_sequences`` must be sorted."""
    return bisect_right(capture_sequences, lower) < bisect_left(capture_sequences, upper)


def _window_bounds_by_session(
    *,
    context: OrderContext,
    position: int,
    anchor_obf_index_by_position: Mapping[int, int],
) -> dict[str, tuple[int, int]]:
    """Narrowest capture interval the nearest settled neighbours leave open, per session.

    Anchors repeat, so each bound is the occurrence closest to the other anchor, not the extreme one.
    """
    before_position = max(
        (anchor for anchor in anchor_obf_index_by_position if anchor < position), default=None
    )
    after_position = min(
        (anchor for anchor in anchor_obf_index_by_position if anchor > position), default=None
    )
    if before_position is None or after_position is None:
        return {}
    captures = context.capture_sequences_by_obf_index
    before_by_session = captures.get(anchor_obf_index_by_position[before_position], {})
    after_by_session = captures.get(anchor_obf_index_by_position[after_position], {})
    bounds_by_session: dict[str, tuple[int, int]] = {}
    for session_id in before_by_session.keys() & after_by_session.keys():
        before_sequences = before_by_session[session_id]
        upper_bound = min(
            (sequence for sequence in after_by_session[session_id] if sequence > min(before_sequences)),
            default=None,
        )
        if upper_bound is not None:
            lower_bound = max(sequence for sequence in before_sequences if sequence < upper_bound)
            bounds_by_session[session_id] = (lower_bound, upper_bound)
    return bounds_by_session


def _apply_support_to_scores(*, context: OrderContext, supports_by_cell: Mapping[Cell, list[float]]) -> None:
    """Reward the supported cells, and push the rows that failed to back a supported class down."""
    supports_by_candidate: defaultdict[int, dict[int, float]] = defaultdict(dict)
    for (non_obf_index, candidate_index), supports in supports_by_cell.items():
        supports_by_candidate[candidate_index][non_obf_index] = sum(supports) / len(supports)

    row_count = context.scores_matrix.shape[0]
    for candidate_index, support_by_non_obf in supports_by_candidate.items():
        if context.is_pinned_obf(candidate_index):
            continue
        best_support = max(support_by_non_obf.values())
        unsupported_share = np.full(row_count, best_support)
        for non_obf_index, support in support_by_non_obf.items():
            unsupported_share[non_obf_index] = best_support - support
        context.scores_matrix[:, candidate_index] *= 1.0 - unsupported_share * _MAX_COMPETITOR_PENALTY
        for non_obf_index, support in support_by_non_obf.items():
            context.scores_matrix[non_obf_index, candidate_index] *= (
                _MIN_MULTIPLIER + support * _MULTIPLIER_SPREAD
            )


def _apply_sole_window_candidates(
    *, context: OrderContext, non_obf_indexes_by_window_obf_index: Mapping[int, set[int]]
) -> None:
    """Give each sole window candidate its column and its row, the way a pin would.

    Boosting the cell is not enough: a class moved out of its package loses more on assembly and
    group similarity than any multiplier here can recover. Contested claims are dropped.
    """
    for obf_index, non_obf_indexes in non_obf_indexes_by_window_obf_index.items():
        if len(non_obf_indexes) != 1:
            continue
        non_obf_index = next(iter(non_obf_indexes))
        retained_score = float(context.scores_matrix[non_obf_index, obf_index])
        if retained_score <= 0.0:
            continue
        context.scores_matrix[:, obf_index] = 0.0
        context.scores_matrix[non_obf_index, :] = 0.0
        context.scores_matrix[non_obf_index, obf_index] = retained_score
