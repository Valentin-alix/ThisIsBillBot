from unittest.mock import patch

import numpy as np
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.matching_builders import (
    build_prepared_scores_for_test,
    number_nested_signature,
    number_root_signature,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_message_lookup,
)
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.signatures import (
    builder_structure_similarity_context,
)

from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from proto_mapper_assembly.matching.score_preparation import build_static_score_data
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestPinnedPairOverrides:
    def test_build_static_score_data_forces_zero_score_pinned_pair_to_one(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_pinned = number_nested_signature("Outer.Pinned", parent_name="Outer", name="Pinned")
        obf_other = number_root_signature("obf_other", name="OtherObf")
        clear_pinned = number_root_signature("ClearPinned")
        clear_other = number_nested_signature("Parent.OtherClear", parent_name="Parent", name="OtherClear")

        score_data = build_static_score_data(
            obf_signatures=[obf_pinned, obf_other],
            non_obf_signatures=[clear_pinned, clear_other],
            pinned_pairs_config=PinnedPairsConfig(
                pairs=[PinnedPair(obf="Outer.Pinned", non_obf="ClearPinned")]
            ),
            runtime_data_store=runtime_data_store,
            structure_context=builder_structure_similarity_context(
                left_signatures=[obf_pinned, obf_other],
                right_signatures=[clear_pinned, clear_other],
            ),
        )

        assert score_data.structure_scores_matrix[0, 0] == 0.0
        assert score_data.assembly_scores_matrix[0, 0] == 0.0
        assert score_data.static_scores_matrix[0, 0] == 1.0
        assert score_data.static_scores_matrix[0, 1] == 0.0
        assert score_data.static_scores_matrix[1, 0] == 0.0

    def test_build_prepared_scores_restores_pinned_pair_before_and_after_mask(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_signature = number_nested_signature("Outer.Pinned", parent_name="Outer", name="Pinned")
        non_obf_signature = number_root_signature("ClearPinned")
        obf_messages_by_cls = build_message_lookup([obf_signature.dump_cs_msg])
        non_obf_messages_by_cls = build_message_lookup([non_obf_signature.dump_cs_msg])
        workspace = build_matching_workspace(
            obf_signatures=[obf_signature],
            non_obf_signatures=[non_obf_signature],
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
        )
        pinned_pairs = PinnedPairsConfig(pairs=[PinnedPair(obf="Outer.Pinned", non_obf="ClearPinned")])

        def _mask_with_assertion(*, workspace: object, base_scores_matrix: np.ndarray) -> np.ndarray:
            del workspace
            assert base_scores_matrix[0, 0] == 1.0
            return np.zeros_like(base_scores_matrix)

        with (
            patch(
                "proto_mapper_assembly.matching.runtime_rescore.build_runtime_field_validator_confidence",
                return_value=0.0,
            ),
            patch(
                "proto_mapper_assembly.matching.static_scores.build_prospective_constraint_mask",
                side_effect=_mask_with_assertion,
            ),
        ):
            prepared_scores = build_prepared_scores_for_test(
                workspace=workspace,
                obf_messages_by_cls=obf_messages_by_cls,
                non_obf_messages_by_cls=non_obf_messages_by_cls,
                runtime_data_store=runtime_data_store,
                pinned_pairs_config=pinned_pairs,
                signature_overrides_by_non_obf_cls={},
                obf_enum_signatures_by_name={},
                non_obf_enum_signatures_by_name={},
                obf_access_trace=EMPTY_ACCESS_TRACE,
                non_obf_access_trace=EMPTY_ACCESS_TRACE,
            )

        assert prepared_scores.final_scores_matrix[0, 0] == 1.0
