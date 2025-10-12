from unittest.mock import Mock, patch

import numpy as np
from DBDofusUnity.proto_mapper_assembly.interfaces.assembly_access import AccessTraceDocument
from DBDofusUnity.proto_mapper_assembly.matching.runtime_rescore import (
    RuntimeCandidateIndexes,
    _iter_runtime_candidate_indexes,
)
from DBDofusUnity.proto_mapper_assembly.matching.score_preparation import (
    _blend_handler_registration_similarity,
)
from DBDofusUnity.proto_mapper_assembly.matching.static_scores import build_static_score_data
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import (
    number_signature,
    simple_signature,
    simple_workspace,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    build_verified_mapping,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import (
    builder_structure_similarity_context,
)


class TestStaticScorePreparation:
    def test_build_static_score_data_skips_full_static_scoring_for_low_structure_pairs(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf = simple_signature("obf")
        non_obf = number_signature("clear")

        with patch(
            "DBDofusUnity.proto_mapper_assembly.matching.static_scores.compute_message_similarity"
        ) as mock_build_full_score:
            score_data = build_static_score_data(
                obf_signatures=[obf],
                non_obf_signatures=[non_obf],
                pinned_pairs_config=build_verified_mapping(),
                runtime_data_store=runtime_data_store,
                structure_context=builder_structure_similarity_context(
                    left_signatures=[obf],
                    right_signatures=[non_obf],
                ),
            )

        mock_build_full_score.assert_not_called()
        assert score_data.structure_scores_matrix[0, 0] == 0.0
        assert score_data.assembly_scores_matrix[0, 0] == 0.0
        assert score_data.static_scores_matrix[0, 0] == 0.0

    def test_runtime_candidate_iteration_keeps_candidates_inside_adaptive_margin(self) -> None:
        indexes = _iter_runtime_candidate_indexes(scores_matrix=np.array([[0.9], [0.86], [0.84], [0.88]]))

        assert indexes == (
            RuntimeCandidateIndexes(0, 0),
            RuntimeCandidateIndexes(3, 0),
            RuntimeCandidateIndexes(1, 0),
            RuntimeCandidateIndexes(2, 0),
        )

    def test_runtime_candidate_iteration_keeps_at_most_ten_candidates(self) -> None:
        scores = np.arange(12, dtype=float).reshape(12, 1) / 100

        indexes = _iter_runtime_candidate_indexes(scores_matrix=scores)

        assert len(indexes) == 10

    def test_handler_registration_similarity_is_bilateral_and_bounded(self) -> None:
        workspace = simple_workspace(
            obf_classes=("obf_event",),
            non_obf_classes=("ClearEvent", "OtherEvent"),
        )
        runtime_data_store = Mock(spec=RuntimeDataStore)
        runtime_data_store.get_normalized_content_for_obf_message.return_value = ({"from_server": True},)
        obf_access_trace = AccessTraceDocument.model_validate(
            {
                "functions_by_address": {
                    "0x1": {
                        "start_address": 1,
                        "end_address": 2,
                        "size": 1,
                        "access_infos": [
                            {
                                "type": "handler_registration",
                                "access_kind": "register",
                                "cls": "obf_event",
                                "handler_method": "Handle",
                                "method_info_address": 1,
                                "filter_typeinfo_address": 2,
                                "index_in_function": 0,
                                "instruction_address": 1,
                                "handler_function_address": 3,
                                "registration_ordinal": 0,
                            }
                        ],
                        "opcode_histogram": {},
                        "aliases": [],
                        "stable_callees": [],
                        "cfg_stats": None,
                    }
                }
            }
        )
        non_obf_access_trace = obf_access_trace.model_copy(
            update={
                "functions_by_address": {
                    "0x1": obf_access_trace.functions_by_address["0x1"].model_copy(
                        update={
                            "access_infos": [
                                obf_access_trace.functions_by_address["0x1"]
                                .access_infos[0]
                                .model_copy(update={"cls": "ClearEvent"})
                            ]
                        }
                    )
                }
            }
        )

        adjusted_scores = _blend_handler_registration_similarity(
            workspace=workspace,
            scores_matrix=np.array([[0.8], [0.8]]),
            obf_messages_by_cls={
                signature.message_cls: signature.dump_cs_msg for signature in workspace.obf_signatures
            },
            runtime_data_store=runtime_data_store,
            obf_access_trace=obf_access_trace,
            non_obf_access_trace=non_obf_access_trace,
        )

        assert np.isclose(adjusted_scores[0, 0], 0.85)
        assert adjusted_scores[1, 0] == 0.8
