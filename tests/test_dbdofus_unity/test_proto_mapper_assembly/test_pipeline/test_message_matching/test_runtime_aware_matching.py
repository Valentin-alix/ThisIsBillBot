from pathlib import Path

import numpy as np
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import typed_dump_field
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_message_lookup,
    build_verified_mapping,
    field_signature,
    message_signature,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_builders import runtime_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_store import seed_runtime_content
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import BOOLEAN_SHAPE, NUMBER_SHAPE
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import declared_field_signature

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import (
    match_messages_for_test,
)

from proto_mapper_assembly.interfaces.assembly_access import MessageAccessSignature
from proto_mapper_assembly.interfaces.capture_sequence_order import CaptureOrderIndex
from proto_mapper_assembly.interfaces.capture_sequence_hints import (
    CaptureSequence,
    CaptureSequenceHintsConfig,
)
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, DumpCSMessageField, FieldKey
from proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from proto_mapper_assembly.interfaces.matching import MatchResult
from proto_mapper_assembly.matching.capture_sequence_order import (
    apply_capture_sequence_order_scores,
)
from proto_mapper_assembly.matching.iterative_store import IterativeMatchingStore
from proto_mapper_assembly.matching.workspace import build_matching_workspace
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestRuntimeAwareMatching:
    def _match_sequence_order_candidates(
        self,
        *,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> tuple[MatchResult, ...]:
        before_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SequenceHintRequest",
            fields=[
                typed_dump_field(
                    field_name="value_",
                    property_name="Value",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        after_message = before_message.model_copy(update={"name": "SequenceHintEvent"})
        obf_messages = [
            DumpCSMessage(
                file_descriptor="GameReflection",
                name=candidate_name,
                fields=[
                    typed_dump_field(
                        field_name="a",
                        property_name="Faaa",
                        normalized_type="int",
                        category=FieldCategoryEnum.NUMBER,
                        offset=0x18,
                    )
                ],
            )
            for candidate_name in ("good_before", "bad_before", "good_after", "bad_after")
        ]
        seed_runtime_content(
            tmp_path,
            {
                "good_before": [
                    runtime_entry({"faaa": 10}, capture_sequence=10, capture_session_id="session-a"),
                    runtime_entry({"faaa": 10}, capture_sequence=10, capture_session_id="session-b"),
                ],
                "bad_before": [
                    runtime_entry({"faaa": 10}, capture_sequence=100, capture_session_id="session-a"),
                    runtime_entry({"faaa": 10}, capture_sequence=100, capture_session_id="session-b"),
                ],
                "good_after": [
                    runtime_entry(
                        {"faaa": 10},
                        from_server=True,
                        capture_sequence=20,
                        capture_session_id="session-a",
                    ),
                    runtime_entry(
                        {"faaa": 10},
                        from_server=True,
                        capture_sequence=20,
                        capture_session_id="session-b",
                    ),
                ],
                "bad_after": [
                    runtime_entry(
                        {"faaa": 10},
                        from_server=True,
                        capture_sequence=5,
                        capture_session_id="session-a",
                    ),
                    runtime_entry(
                        {"faaa": 10},
                        from_server=True,
                        capture_sequence=5,
                        capture_session_id="session-b",
                    ),
                ],
            },
        )
        signature_fields = [declared_field_signature(NUMBER_SHAPE)]
        obf_signatures = [
            self._build_sequence_hint_obf_signature(
                obf_message=obf_message,
                signature_fields=signature_fields,
            )
            for obf_message in obf_messages
        ]
        for signature_index, obf_signature in enumerate(obf_signatures):
            from_server = signature_index >= 2
            seed_entry = runtime_data_store.merged_content_by_name.root[obf_signature.message_cls][0]
            assert seed_entry.from_server is from_server
        return match_messages_for_test(
            obf_signatures,
            [
                message_signature(
                    "SequenceHintRequest",
                    declared_field_signatures=signature_fields,
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "value_")}),
                    dump_cs_msg=before_message,
                ),
                message_signature(
                    "SequenceHintEvent",
                    declared_field_signatures=signature_fields,
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "value_")}),
                    dump_cs_msg=after_message,
                ),
            ],
            obf_messages_by_cls=build_message_lookup(obf_messages),
            non_obf_messages_by_cls=build_message_lookup([before_message, after_message]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(
                sequences=(
                    CaptureSequence(
                        name="request_event",
                        messages=("SequenceHintRequest", "SequenceHintEvent"),
                    ),
                )
            ),
        )

    def _build_sequence_hint_obf_signature(
        self,
        *,
        obf_message: DumpCSMessage,
        signature_fields: list[DumpCSMessageField],
    ) -> MessageAccessSignature:
        return message_signature(
            obf_message.name,
            declared_field_signatures=signature_fields,
            field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(0x18, "a")}),
            dump_cs_msg=obf_message,
        )

    def test_runtime_prefers_valid_candidate_over_stronger_invalid_candidate(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="StatedElement",
            fields=[
                typed_dump_field(
                    field_name="element_id_",
                    property_name="ElementId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="cell_id_",
                    property_name="CellId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x1C,
                ),
                typed_dump_field(
                    field_name="state_",
                    property_name="State",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
                typed_dump_field(
                    field_name="on_current_map_",
                    property_name="OnCurrentMap",
                    normalized_type="bool",
                    category=FieldCategoryEnum.BOOLEAN,
                    offset=0x24,
                ),
            ],
        )
        bad_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="bad_obf",
            fields=[
                typed_dump_field(
                    field_name="a",
                    property_name="Fnjr",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="b",
                    property_name="Fnjq",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x1C,
                ),
                typed_dump_field(
                    field_name="c",
                    property_name="Fnjt",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
                typed_dump_field(
                    field_name="d",
                    property_name="Fnjp",
                    normalized_type="bool",
                    category=FieldCategoryEnum.BOOLEAN,
                    offset=0x24,
                ),
            ],
        )
        good_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="good_obf",
            fields=[
                typed_dump_field(
                    field_name="a",
                    property_name="Fnjr",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="b",
                    property_name="Fnjq",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x1C,
                ),
                typed_dump_field(
                    field_name="c",
                    property_name="Fnjt",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
                typed_dump_field(
                    field_name="d",
                    property_name="Fnjp",
                    normalized_type="bool",
                    category=FieldCategoryEnum.BOOLEAN,
                    offset=0x24,
                ),
            ],
        )
        declared_fields = [
            declared_field_signature(NUMBER_SHAPE),
            declared_field_signature(NUMBER_SHAPE),
            declared_field_signature(NUMBER_SHAPE),
            declared_field_signature(BOOLEAN_SHAPE),
        ]
        seed_runtime_content(
            tmp_path,
            {
                "bad_obf": [
                    runtime_entry({"fnjr": 10, "fnjq": 1, "fnjt": 999, "fnjp": True}, is_root_msg=False),
                    runtime_entry({"fnjr": 11, "fnjq": 2, "fnjt": 999, "fnjp": True}, is_root_msg=False),
                    runtime_entry({"fnjr": 12, "fnjq": 3, "fnjt": 999, "fnjp": True}, is_root_msg=False),
                ],
                "good_obf": [
                    runtime_entry({"fnjr": 10, "fnjq": 1, "fnjt": 0, "fnjp": True}, is_root_msg=False),
                    runtime_entry({"fnjr": 11, "fnjq": 2, "fnjt": 0, "fnjp": True}, is_root_msg=False),
                    runtime_entry({"fnjr": 12, "fnjq": 3, "fnjt": 0, "fnjp": True}, is_root_msg=False),
                ],
            },
        )

        matches = match_messages_for_test(
            [
                message_signature(
                    "bad_obf",
                    declared_field_signatures=declared_fields,
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x1C, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                        field_signature(0x24, BOOLEAN_SHAPE),
                    ],
                    live_field_keys=frozenset(
                        {FieldKey(0x18, "a"), FieldKey(0x1C, "b"), FieldKey(0x20, "c"), FieldKey(0x24, "d")}
                    ),
                    dump_cs_msg=bad_message,
                ),
                message_signature(
                    "good_obf",
                    declared_field_signatures=declared_fields,
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x1C, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                        field_signature(0x24, BOOLEAN_SHAPE),
                    ],
                    live_field_keys=frozenset(
                        {FieldKey(0x18, "a"), FieldKey(0x1C, "b"), FieldKey(0x20, "c"), FieldKey(0x24, "d")}
                    ),
                    dump_cs_msg=good_message,
                ),
            ],
            [
                message_signature(
                    "StatedElement",
                    declared_field_signatures=declared_fields,
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x1C, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                        field_signature(0x24, BOOLEAN_SHAPE),
                    ],
                    live_field_keys=frozenset(
                        {
                            FieldKey(0x18, "element_id_"),
                            FieldKey(0x1C, "cell_id_"),
                            FieldKey(0x20, "state_"),
                            FieldKey(0x24, "on_current_map_"),
                        }
                    ),
                    dump_cs_msg=non_obf_message,
                ),
            ],
            obf_messages_by_cls=build_message_lookup([bad_message, good_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        assert len(matches) == 1
        assert matches[0].obf_signature.message_cls == "good_obf"
        assert matches[0].runtime_confidence == 1.0
        assert matches[0].score > 0.5

    def test_capture_sequence_order_prefers_coherent_candidate_pair(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        matches = self._match_sequence_order_candidates(
            runtime_data_store=runtime_data_store,
            tmp_path=tmp_path,
        )

        assert {
            match.non_obf_signature.message_cls: match.obf_signature.message_cls for match in matches
        } == {"SequenceHintRequest": "good_before", "SequenceHintEvent": "good_after"}

    def test_capture_sequence_order_scores_a_complete_three_message_chain(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_messages = [
            DumpCSMessage(file_descriptor="GameReflection", name=message_name)
            for message_name in ("ClearFirst", "ClearMiddle", "ClearLast")
        ]
        obf_messages = [
            DumpCSMessage(file_descriptor="GameReflection", name=message_name)
            for message_name in (
                "good_first",
                "bad_first",
                "good_middle",
                "bad_middle",
                "good_last",
                "bad_last",
            )
        ]
        seed_runtime_content(
            tmp_path,
            {
                "good_first": [
                    runtime_entry({}, capture_sequence=10, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "bad_first": [
                    runtime_entry({}, capture_sequence=100, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "good_middle": [
                    runtime_entry({}, capture_sequence=15, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "bad_middle": [
                    runtime_entry({}, capture_sequence=1, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "good_last": [
                    runtime_entry({}, capture_sequence=20, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "bad_last": [
                    runtime_entry({}, capture_sequence=5, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
            },
        )
        workspace = build_matching_workspace(
            obf_signatures=[
                message_signature(message.name, [], dump_cs_msg=message) for message in obf_messages
            ],
            non_obf_signatures=[
                message_signature(message.name, [], dump_cs_msg=message) for message in non_obf_messages
            ],
            obf_messages_by_cls=build_message_lookup(obf_messages),
            non_obf_messages_by_cls=build_message_lookup(non_obf_messages),
        )
        scores_matrix = np.array(
            [
                [0.8, 0.8, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.8, 0.8, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.8, 0.8],
            ]
        )

        apply_capture_sequence_order_scores(
            workspace=workspace,
            scores_matrix=scores_matrix,
            matching_store=IterativeMatchingStore(),
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=build_verified_mapping(),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(
                sequences=(
                    CaptureSequence(
                        name="three_messages",
                        messages=("ClearFirst", "ClearMiddle", "ClearLast"),
                    ),
                )
            ),
        )

        assert scores_matrix[0, 0] > scores_matrix[0, 1]
        assert scores_matrix[1, 2] > scores_matrix[1, 3]
        assert scores_matrix[2, 4] > scores_matrix[2, 5]
        assert scores_matrix[0, 1] < 0.8
        assert scores_matrix[1, 3] < 0.8
        assert scores_matrix[2, 5] < 0.8

    def test_capture_sequence_order_includes_captured_candidate_outside_static_limit(
        self,
        runtime_data_store: RuntimeDataStore,
        tmp_path: Path,
    ) -> None:
        non_obf_messages = [
            DumpCSMessage(file_descriptor="GameReflection", name=message_name)
            for message_name in ("ClearBefore", "ClearAfter")
        ]
        obf_messages = [
            DumpCSMessage(file_descriptor="GameReflection", name=f"uncaptured_{candidate_index}")
            for candidate_index in range(5)
        ]
        captured_before = DumpCSMessage(
            file_descriptor="GameReflection",
            name="captured_before",
        )
        captured_after = DumpCSMessage(
            file_descriptor="GameReflection",
            name="captured_after",
        )
        obf_messages.extend((captured_before, captured_after))
        seed_runtime_content(
            tmp_path,
            {
                "captured_before": [
                    runtime_entry({}, capture_sequence=10, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
                "captured_after": [
                    runtime_entry({}, capture_sequence=20, capture_session_id=session_id)
                    for session_id in ("session-a", "session-b")
                ],
            },
        )
        workspace = build_matching_workspace(
            obf_signatures=[
                message_signature(message.name, [], dump_cs_msg=message) for message in obf_messages
            ],
            non_obf_signatures=[
                message_signature(message.name, [], dump_cs_msg=message) for message in non_obf_messages
            ],
            obf_messages_by_cls=build_message_lookup(obf_messages),
            non_obf_messages_by_cls=build_message_lookup(non_obf_messages),
        )
        scores_matrix = np.array(
            [
                [0.90, 0.89, 0.88, 0.87, 0.86, 0.60, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.80],
            ]
        )

        apply_capture_sequence_order_scores(
            workspace=workspace,
            scores_matrix=scores_matrix,
            matching_store=IterativeMatchingStore(),
            capture_order_index=CaptureOrderIndex.build(
                workspace=workspace,
                pinned_pairs_config=build_verified_mapping(),
                runtime_data_store=runtime_data_store,
            ),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(
                sequences=(
                    CaptureSequence(
                        name="captured_candidates",
                        messages=("ClearBefore", "ClearAfter"),
                    ),
                )
            ),
        )

        assert scores_matrix[0, 5] > 0.60
        assert scores_matrix[1, 6] > 0.80
