from pathlib import Path

import numpy as np
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import message_signature
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_store import seed_runtime_content

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from proto_mapper_assembly.interfaces.capture_sequence_hints import (
    CaptureSequence,
    CaptureSequenceHintsConfig,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPairsConfig
from proto_mapper_assembly.matching.capture_sequence_order import apply_capture_sequence_order_scores
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore

_SESSION = "session_a"


def _named_message(message_cls: str) -> DumpCSMessage:
    return DumpCSMessage(file_descriptor="GameReflection", name=message_cls)


def _named_signature(message_cls: str) -> MessageAccessSignature:
    return message_signature(message_cls, [], dump_cs_msg=_named_message(message_cls))


class TestCaptureSequenceOrder:
    def test_sole_class_captured_between_settled_neighbours_wins_over_a_better_scoring_rival(
        self, tmp_path: Path, runtime_data_store: RuntimeDataStore
    ) -> None:
        """The displaced-class case: only the capture position can tell `obf_target` apart.

        `obf_rival` looks far better on every static signal, the way a same-shaped sibling sitting in
        the expected package block does. Only `obf_target` was captured between the two neighbours
        the hint names, so it takes the pair even though it scores nine times lower.
        """
        obf_classes = ("obf_before", "obf_target", "obf_after", "obf_rival")
        non_obf_classes = ("Before", "Target", "After", "Other")
        seed_runtime_content(
            tmp_path,
            {
                "obf_before": [{"capture_sequence": 10, "capture_session_id": _SESSION}],
                "obf_target": [{"capture_sequence": 11, "capture_session_id": _SESSION}],
                "obf_after": [{"capture_sequence": 12, "capture_session_id": _SESSION}],
                "obf_rival": [{"capture_sequence": 90, "capture_session_id": _SESSION}],
            },
        )
        workspace = build_matching_workspace(
            obf_signatures=[_named_signature(message_cls) for message_cls in obf_classes],
            non_obf_signatures=[_named_signature(message_cls) for message_cls in non_obf_classes],
            obf_messages_by_cls={message_cls: _named_message(message_cls) for message_cls in obf_classes},
            non_obf_messages_by_cls={
                message_cls: _named_message(message_cls) for message_cls in non_obf_classes
            },
        )
        obf_index = workspace.signature_indexes.obf_index_by_cls
        non_obf_index = workspace.signature_indexes.non_obf_index_by_cls
        scores_matrix = np.zeros((len(non_obf_classes), len(obf_classes)))
        scores_matrix[non_obf_index["Before"], obf_index["obf_before"]] = 0.9
        scores_matrix[non_obf_index["After"], obf_index["obf_after"]] = 0.9
        scores_matrix[non_obf_index["Target"], obf_index["obf_rival"]] = 0.9
        scores_matrix[non_obf_index["Target"], obf_index["obf_target"]] = 0.1
        scores_matrix[non_obf_index["Other"], obf_index["obf_target"]] = 0.8

        apply_capture_sequence_order_scores(
            workspace=workspace,
            scores_matrix=scores_matrix,
            matching_store=IterativeMatchingStore(
                confirmed_obf_by_non_obf={"Before": "obf_before", "After": "obf_after"}
            ),
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=PinnedPairsConfig(pairs=[]),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(
                sequences=(CaptureSequence(name="probe", messages=("Before", "Target", "After")),)
            ),
        )

        # The pair survives alone in both its row and its column, so the assignment has no choice
        # left to make, whatever the remaining score is worth.
        assert scores_matrix[non_obf_index["Target"], obf_index["obf_target"]] > 0.0
        assert scores_matrix[non_obf_index["Target"], obf_index["obf_rival"]] == 0.0
        assert scores_matrix[non_obf_index["Other"], obf_index["obf_target"]] == 0.0

    def test_ambiguous_window_leaves_the_competition_alone(
        self, tmp_path: Path, runtime_data_store: RuntimeDataStore
    ) -> None:
        """Two captured classes fit the interval, so nothing is claimed and scores stay comparable."""
        obf_classes = ("obf_before", "obf_target", "obf_after", "obf_rival")
        non_obf_classes = ("Before", "Target", "After", "Other")
        seed_runtime_content(
            tmp_path,
            {
                "obf_before": [{"capture_sequence": 10, "capture_session_id": _SESSION}],
                "obf_target": [{"capture_sequence": 11, "capture_session_id": _SESSION}],
                "obf_rival": [{"capture_sequence": 11, "capture_session_id": _SESSION}],
                "obf_after": [{"capture_sequence": 12, "capture_session_id": _SESSION}],
            },
        )
        workspace = build_matching_workspace(
            obf_signatures=[_named_signature(message_cls) for message_cls in obf_classes],
            non_obf_signatures=[_named_signature(message_cls) for message_cls in non_obf_classes],
            obf_messages_by_cls={message_cls: _named_message(message_cls) for message_cls in obf_classes},
            non_obf_messages_by_cls={
                message_cls: _named_message(message_cls) for message_cls in non_obf_classes
            },
        )
        obf_index = workspace.signature_indexes.obf_index_by_cls
        non_obf_index = workspace.signature_indexes.non_obf_index_by_cls
        scores_matrix = np.zeros((len(non_obf_classes), len(obf_classes)))
        scores_matrix[non_obf_index["Before"], obf_index["obf_before"]] = 0.9
        scores_matrix[non_obf_index["After"], obf_index["obf_after"]] = 0.9
        scores_matrix[non_obf_index["Target"], obf_index["obf_rival"]] = 0.9
        scores_matrix[non_obf_index["Target"], obf_index["obf_target"]] = 0.1
        scores_matrix[non_obf_index["Other"], obf_index["obf_target"]] = 0.8

        apply_capture_sequence_order_scores(
            workspace=workspace,
            scores_matrix=scores_matrix,
            matching_store=IterativeMatchingStore(
                confirmed_obf_by_non_obf={"Before": "obf_before", "After": "obf_after"}
            ),
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=PinnedPairsConfig(pairs=[]),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(
                sequences=(CaptureSequence(name="probe", messages=("Before", "Target", "After")),)
            ),
        )

        assert scores_matrix[non_obf_index["Target"], obf_index["obf_rival"]] > 0.0
        assert scores_matrix[non_obf_index["Other"], obf_index["obf_target"]] > 0.0
