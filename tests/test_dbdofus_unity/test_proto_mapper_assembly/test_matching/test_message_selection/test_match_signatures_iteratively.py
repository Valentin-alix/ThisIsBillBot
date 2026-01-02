import numpy as np
import pytest
from tests.fixtures.proto_mapper.matching_builders import (
    prepared_scores_from_matrix,
    select_best_signature_pair,
    simple_signature,
)
from tests.fixtures.proto_mapper.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_verified_mapping,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping import FieldMappingContext
from DBDofusUnity.proto_mapper_assembly.interfaces.matching_inputs import MatchingInputs, MatchingRunConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from DBDofusUnity.proto_mapper_assembly.matching.message_selection import match_signatures_iteratively
from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestMatchSignaturesIteratively:
    def test_ambiguous_pair_does_not_hide_an_unrelated_confident_pair(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        obf_gamma = simple_signature("obf_gamma")
        clear_alpha = simple_signature("ClearAlpha")
        clear_beta = simple_signature("ClearBeta")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta, obf_gamma],
            non_obf_signatures=[clear_alpha, clear_beta],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        selected_pair = select_best_signature_pair(
            workspace=workspace,
            scores_matrix=np.array([[0.9, 0.88, 0.1], [0.1, 0.1, 0.8]]),
            available_non_obf=[clear_alpha, clear_beta],
            available_obf=[obf_alpha, obf_beta, obf_gamma],
            roots_only=False,
            pinned_pairs_config=build_verified_mapping(),
        )

        assert selected_pair is not None
        assert selected_pair.non_obf_signature is clear_beta
        assert selected_pair.obf_signature is obf_gamma

    def test_ambiguous_competitors_are_left_unmatched(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        clear_alpha = simple_signature("ClearAlpha")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta],
            non_obf_signatures=[clear_alpha],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        selected_pair = select_best_signature_pair(
            workspace=workspace,
            scores_matrix=np.array([[0.9, 0.88]]),
            available_non_obf=[clear_alpha],
            available_obf=[obf_alpha, obf_beta],
            roots_only=False,
            pinned_pairs_config=build_verified_mapping(),
        )

        assert selected_pair is None

    def test_global_assignment_avoids_greedy_pairing_trap(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        clear_alpha = simple_signature("ClearAlpha")
        clear_beta = simple_signature("ClearBeta")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta],
            non_obf_signatures=[clear_alpha, clear_beta],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        selected_pair = select_best_signature_pair(
            workspace=workspace,
            scores_matrix=np.array([[0.90, 0.80], [0.85, 0.10]]),
            available_non_obf=[clear_alpha, clear_beta],
            available_obf=[obf_alpha, obf_beta],
            roots_only=False,
            pinned_pairs_config=build_verified_mapping(),
        )

        assert selected_pair is not None
        assert selected_pair.non_obf_signature is clear_beta
        assert selected_pair.obf_signature is obf_alpha

    def test_unique_mutual_best_survives_a_small_assignment_margin(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        clear_alpha = simple_signature("ClearAlpha")
        clear_beta = simple_signature("ClearBeta")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta],
            non_obf_signatures=[clear_alpha, clear_beta],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        selected_pair = select_best_signature_pair(
            workspace=workspace,
            scores_matrix=np.array([[0.78, 0.75], [0.74, 0.72]]),
            available_non_obf=[clear_alpha, clear_beta],
            available_obf=[obf_alpha, obf_beta],
            roots_only=False,
            pinned_pairs_config=build_verified_mapping(),
        )

        assert selected_pair is not None
        assert selected_pair.non_obf_signature is clear_alpha
        assert selected_pair.obf_signature is obf_alpha

    def test_symmetric_assignment_remains_unmatched(self) -> None:
        obf_alpha = simple_signature("obf_alpha")
        obf_beta = simple_signature("obf_beta")
        clear_alpha = simple_signature("ClearAlpha")
        clear_beta = simple_signature("ClearBeta")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha, obf_beta],
            non_obf_signatures=[clear_alpha, clear_beta],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        selected_pair = select_best_signature_pair(
            workspace=workspace,
            scores_matrix=np.full((2, 2), 0.9),
            available_non_obf=[clear_alpha, clear_beta],
            available_obf=[obf_alpha, obf_beta],
            roots_only=False,
            pinned_pairs_config=build_verified_mapping(),
        )

        assert selected_pair is None

    @pytest.mark.parametrize(
        ("scores_matrix", "matching_store", "score_by_pair"),
        [
            (
                np.array([[0.9]]),
                IterativeMatchingStore(confirmed_non_obf_by_obf={"obf_alpha": "SomeOtherClear"}),
                {MatchPairKey("obf_alpha", "ClearAlpha"): 0.9},
            ),
            (
                np.zeros((1, 1)),
                IterativeMatchingStore(),
                {MatchPairKey("obf_alpha", "ClearAlpha"): 0.0},
            ),
        ],
    )
    def test_returns_empty_when_candidate_cannot_be_confirmed(
        self,
        scores_matrix: np.ndarray,
        matching_store: IterativeMatchingStore,
        score_by_pair: dict[MatchPairKey, float],
        runtime_data_store: RuntimeDataStore,
    ) -> None:
        obf_alpha = simple_signature("obf_alpha")
        clear_alpha = simple_signature("ClearAlpha")
        workspace = build_matching_workspace(
            obf_signatures=[obf_alpha],
            non_obf_signatures=[clear_alpha],
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )

        matches = match_signatures_iteratively(
            workspace=workspace,
            prepared_scores=prepared_scores_from_matrix(scores_matrix),
            matching_store=matching_store,
            inputs=MatchingInputs(
                obf_messages_by_cls={},
                non_obf_messages_by_cls={},
                obf_signatures_by_cls={obf_alpha.message_cls: obf_alpha},
                non_obf_signatures_by_cls={clear_alpha.message_cls: clear_alpha},
                signature_overrides_by_non_obf_cls={},
                obf_enum_signatures_by_name={},
                non_obf_enum_signatures_by_name={},
                obf_access_trace=EMPTY_ACCESS_TRACE,
                non_obf_access_trace=EMPTY_ACCESS_TRACE,
            ),
            run_config=MatchingRunConfig(
                runtime_data_store=runtime_data_store,
                pinned_pairs_config=build_verified_mapping(),
                capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            ),
            field_mapping_context=FieldMappingContext(
                score_by_pair=score_by_pair,
                runtime_data_store=runtime_data_store,
                signature_overrides_by_non_obf_cls={},
                obf_enum_signatures_by_name={},
                non_obf_enum_signatures_by_name={},
                obf_access_trace=EMPTY_ACCESS_TRACE,
                non_obf_access_trace=EMPTY_ACCESS_TRACE,
            ),
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=build_verified_mapping(),
                runtime_data_store=runtime_data_store,
            ),
            available_non_obf_indexes={0},
            available_obf_indexes={0},
            roots_only=False,
        )

        assert matches == []
