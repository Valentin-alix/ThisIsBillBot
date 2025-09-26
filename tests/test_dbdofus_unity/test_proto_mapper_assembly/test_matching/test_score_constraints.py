import numpy as np
import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import (
    prospective_child_constraint_workspace,
    simple_signature,
    simple_workspace,
)

from proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from proto_mapper_assembly.matching.score_constraints import (
    build_adjusted_scores_matrix,
    build_prospective_constraint_mask,
)
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestScoreConstraints:
    @pytest.mark.parametrize(
        ("matching_store", "expected_scores"),
        [
            (
                IterativeMatchingStore(
                    confirmed_obf_by_non_obf={"ClearBeta": "obf_beta"},
                    source_by_obf={"obf_beta": "group_match"},
                ),
                np.array([[0.8, 0.7], [0.0, 0.6]]),
            ),
            (
                IterativeMatchingStore(
                    confirmed_non_obf_by_obf={"obf_alpha": "ClearAlpha"},
                    source_by_obf={"obf_alpha": "group_match"},
                ),
                np.array([[0.9, 0.7], [0.0, 0.6]]),
            ),
            (
                IterativeMatchingStore(
                    inferred_non_obf_by_obf={"obf_beta": "ClearBeta"},
                    inferred_confidence_by_pair={MatchPairKey("obf_beta", "ClearBeta"): 0.8},
                    source_by_obf={"obf_beta": "field_mapping"},
                ),
                np.array([[0.8, 0.0], [0.2, 0.7]]),
            ),
        ],
    )
    def test_build_adjusted_scores_matrix_applies_store_constraints(
        self,
        matching_store: IterativeMatchingStore,
        expected_scores: np.ndarray,
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        workspace = simple_workspace()
        adjusted_scores_matrix = build_adjusted_scores_matrix(
            workspace=workspace,
            base_scores_matrix=np.array([[0.8, 0.7], [0.2, 0.6]]),
            matching_store=matching_store,
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=PinnedPairsConfig(pairs=[]),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )

        np.testing.assert_allclose(adjusted_scores_matrix, expected_scores)

    def test_build_prospective_constraint_mask_keeps_only_children_supported_by_parent_candidates(
        self,
    ) -> None:
        prospective_mask = build_prospective_constraint_mask(
            workspace=prospective_child_constraint_workspace(),
            base_scores_matrix=np.array(
                [
                    [0.5, 0.9],
                    [0.1, 0.8],
                    [0.35, 0.7],
                ]
            ),
        )

        np.testing.assert_array_equal(
            prospective_mask,
            np.array(
                [
                    [1.0, 0.0],
                    [1.0, 1.0],
                    [1.0, 0.0],
                ]
            ),
        )

    def test_build_adjusted_scores_matrix_bonuses_confirmed_pair(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        workspace = build_matching_workspace(
            obf_signatures=[simple_signature("obf_alpha")],
            non_obf_signatures=[simple_signature("ClearAlpha")],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )
        matching_store = IterativeMatchingStore(
            confirmed_non_obf_by_obf={"obf_alpha": "ClearAlpha"},
            confirmed_obf_by_non_obf={"ClearAlpha": "obf_alpha"},
            inferred_non_obf_by_obf={},
            source_by_obf={"obf_alpha": "group_match"},
        )

        adjusted_scores_matrix = build_adjusted_scores_matrix(
            workspace=workspace,
            base_scores_matrix=np.array([[0.95]]),
            matching_store=matching_store,
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=PinnedPairsConfig(pairs=[]),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )

        np.testing.assert_array_equal(adjusted_scores_matrix, np.array([[1.0]]))
