from typing import Any

import numpy as np
from tests.fixtures.proto_mapper.matching_builders import simple_workspace

from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from DBDofusUnity.proto_mapper_assembly.affinities.handler_cohorts import build_handler_cohort_affinity
from DBDofusUnity.proto_mapper_assembly.interfaces.affinity import AffinitySignalInputs
from DBDofusUnity.proto_mapper_assembly.matching.score_preparation import (
    _MASKED_AFFINITY_SIGNALS,
    _blend_masked_affinity,
)

_OBF_CLASSES = ("obf_a1", "obf_a2", "obf_b1")
_NON_OBF_CLASSES = ("ClearA1", "ClearA2", "ClearB1", "ClearUnregistered")
_BASE_SCORES = np.array(
    [
        [0.9, 0.1, 0.1],
        [0.1, 0.9, 0.1],
        [0.1, 0.1, 0.9],
        [0.1, 0.1, 0.1],
    ]
)
_TIED_SIBLING_SCORES = np.array(
    [
        [0.5, 0.5, 0.1],
        [0.5, 0.5, 0.1],
        [0.1, 0.1, 0.9],
        [0.1, 0.1, 0.1],
    ]
)
"""ClearA1/ClearA2 score identically against obf_a1/obf_a2: only the cohort order can separate them."""

_COHORT_WEIGHT = next(signal.weight for signal in _MASKED_AFFINITY_SIGNALS if signal.name == "handler_cohort")


def _access_trace(registrations_by_function: dict[str, list[str]]) -> AccessTraceDocument:
    functions_by_address: dict[str, Any] = {}
    for function_address, registered_classes in registrations_by_function.items():
        functions_by_address[function_address] = {
            "start_address": int(function_address, 16),
            "end_address": int(function_address, 16) + 1,
            "size": 1,
            "access_infos": [
                {
                    "type": "handler_registration",
                    "access_kind": "register",
                    "cls": registered_class,
                    "handler_method": f"Boolean Handle({registered_class})",
                    "method_info_address": index,
                    "filter_typeinfo_address": index,
                    "index_in_function": index,
                    "instruction_address": int(function_address, 16) + index,
                    "handler_function_address": int(function_address, 16) + 0x100 + index,
                    "registration_ordinal": index,
                }
                for index, registered_class in enumerate(registered_classes)
            ],
            "opcode_histogram": {},
            "aliases": [],
            "stable_callees": [],
            "cfg_stats": None,
        }
    return AccessTraceDocument.model_validate({"functions_by_address": functions_by_address})


def _build_affinity() -> tuple[np.ndarray, np.ndarray]:
    return build_handler_cohort_affinity(
        AffinitySignalInputs(
            workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
            base_scores_matrix=_BASE_SCORES,
            obf_access_trace=_access_trace({"0x10": ["obf_a1", "obf_a2"], "0x20": ["obf_b1"]}),
            non_obf_access_trace=_access_trace({"0x30": ["ClearA1", "ClearA2"], "0x40": ["ClearB1"]}),
        )
    )


class TestHandlerCohorts:
    def test_messages_aligned_inside_matched_cohorts_get_affinity(self) -> None:
        affinity_matrix, _ = _build_affinity()

        assert affinity_matrix[0, 0] == 1.0
        assert affinity_matrix[1, 1] == 1.0
        assert affinity_matrix[2, 2] == 1.0

    def test_cohort_siblings_are_ranked_by_registration_order(self) -> None:
        # Sharing a matched cohort keeps most of the reward, but the sibling sitting at the same
        # registration ordinal is ranked above the one that is merely in the same cohort.
        affinity_matrix, _ = _build_affinity()

        assert affinity_matrix[0, 0] > affinity_matrix[0, 1] > affinity_matrix[0, 2]
        assert affinity_matrix[0, 2] == 0.0

    def test_registration_order_breaks_ties_between_indistinguishable_siblings(self) -> None:
        # The real case this exists for: two same-shaped siblings in one cohort that the structural
        # score cannot separate. Registering them in reverse order must flip which pair is rewarded.
        affinity_matrix, _ = build_handler_cohort_affinity(
            AffinitySignalInputs(
                workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
                base_scores_matrix=_TIED_SIBLING_SCORES,
                obf_access_trace=_access_trace({"0x10": ["obf_a2", "obf_a1"], "0x20": ["obf_b1"]}),
                non_obf_access_trace=_access_trace({"0x30": ["ClearA1", "ClearA2"], "0x40": ["ClearB1"]}),
            )
        )

        assert affinity_matrix[0, 1] == 1.0
        assert affinity_matrix[1, 0] == 1.0
        assert affinity_matrix[0, 1] > affinity_matrix[0, 0]

    def test_ordering_is_skipped_when_the_cohorts_lost_too_many_handlers(self) -> None:
        # obf cohort A shrank to a single handler: the ordinals no longer describe the same list, so
        # membership alone is rewarded and every member of the matched cohort is treated equally.
        affinity_matrix, _ = build_handler_cohort_affinity(
            AffinitySignalInputs(
                workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
                base_scores_matrix=_TIED_SIBLING_SCORES,
                obf_access_trace=_access_trace({"0x10": ["obf_a1"], "0x20": ["obf_b1"]}),
                non_obf_access_trace=_access_trace({"0x30": ["ClearA1", "ClearA2"], "0x40": ["ClearB1"]}),
            )
        )

        assert affinity_matrix[0, 0] == 1.0
        assert affinity_matrix[1, 0] == 1.0

    def test_a_decisive_score_still_wins_over_registration_order(self) -> None:
        # Order is a tie-breaker, not an override: the gap penalty is small on purpose, so a pair the
        # structural score is sure about survives a cohort whose ordinals disagree.
        affinity_matrix, _ = build_handler_cohort_affinity(
            AffinitySignalInputs(
                workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
                base_scores_matrix=_BASE_SCORES,
                obf_access_trace=_access_trace({"0x10": ["obf_a2", "obf_a1"], "0x20": ["obf_b1"]}),
                non_obf_access_trace=_access_trace({"0x30": ["ClearA1", "ClearA2"], "0x40": ["ClearB1"]}),
            )
        )

        assert affinity_matrix[0, 0] == 1.0

    def test_messages_crossing_matched_cohorts_lose_affinity(self) -> None:
        affinity_matrix, _ = _build_affinity()

        assert affinity_matrix[0, 2] == 0.0
        assert affinity_matrix[2, 0] == 0.0

    def test_pairs_crossing_two_matched_cohorts_stay_constrained(self) -> None:
        # The mask is per side, not per pair: ClearA1 and obf_b1 sit in two *different* matched
        # cohorts, and the pair must stay masked in so that its zero affinity penalizes the crossing.
        # Narrowing this to "both in the same cohort" would silently disable that penalty.
        _, applicable_mask = _build_affinity()

        assert applicable_mask[0, 2]

    def test_messages_without_registration_are_not_constrained(self) -> None:
        _, applicable_mask = _build_affinity()

        assert not applicable_mask[3].any()
        assert applicable_mask[:3].all()

    def test_empty_trace_constrains_nothing(self) -> None:
        affinity_matrix, applicable_mask = build_handler_cohort_affinity(
            AffinitySignalInputs(
                workspace=simple_workspace(obf_classes=_OBF_CLASSES, non_obf_classes=_NON_OBF_CLASSES),
                base_scores_matrix=_BASE_SCORES,
                obf_access_trace=_access_trace({}),
                non_obf_access_trace=_access_trace({}),
            )
        )

        assert affinity_matrix.shape == _BASE_SCORES.shape
        assert not applicable_mask.any()

    def test_blend_is_bounded_and_leaves_unconstrained_pairs_untouched(self) -> None:
        affinity_matrix, applicable_mask = _build_affinity()

        blended_scores = _blend_masked_affinity(
            message_scores_matrix=_BASE_SCORES,
            affinity_matrix=affinity_matrix,
            applicable_mask=applicable_mask,
            weight=_COHORT_WEIGHT,
        )

        # Sharing a matched cohort lifts the pair, crossing one pushes it down without ever
        # making it unreachable, and a message registering no handler keeps its score as-is.
        assert blended_scores[0, 0] > _BASE_SCORES[0, 0]
        assert 0.0 < blended_scores[0, 2] < _BASE_SCORES[0, 2]
        assert np.isclose(blended_scores[3, 0], _BASE_SCORES[3, 0])
        assert blended_scores[0, 0] > blended_scores[0, 2]
