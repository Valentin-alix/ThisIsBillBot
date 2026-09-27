import numpy as np
import pytest
from tests.fixtures.proto_mapper.field_builders import typed_dump_field
from tests.fixtures.proto_mapper.matching_builders import (
    select_grouped_matches_for_test,
)
from tests.fixtures.proto_mapper.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_message_lookup,
    build_verified_mapping,
    field_signature,
    message_signature,
)
from tests.fixtures.proto_mapper.shapes import MESSAGE_SHAPE, NUMBER_SHAPE
from tests.fixtures.proto_mapper.signatures import declared_field_signature

from DBDofusUnity.proto_mapper_assembly.affinities._group_similarity import get_group_similarity_score
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.matching import PreparedScoreData
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.matching.workspace import build_matching_workspace
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestGroupedMatching:
    def test_group_score_penalizes_rectangular_group_sizes(self) -> None:
        score = get_group_similarity_score(
            similarity_matrix=np.array([[1.0], [0.9]]),
            non_obf_count=2,
            obf_count=1,
        )

        assert score == 0.5

    def test_select_grouped_matches_prefers_best_file_descriptor_pairing(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_signatures = [
            message_signature("obf_x1", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "obf_x"}
            ),
            message_signature("obf_x2", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "obf_x"}
            ),
            message_signature("obf_y1", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "obf_y"}
            ),
        ]
        non_obf_signatures = [
            message_signature("clear_a1", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "group_a"}
            ),
            message_signature("clear_a2", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "group_a"}
            ),
            message_signature("clear_b1", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "group_b"}
            ),
        ]
        workspace = build_matching_workspace(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )
        final_scores_matrix = np.array(
            [
                [0.80, 0.10, 0.20],
                [0.10, 0.79, 0.10],
                [0.30, 0.31, 0.60],
            ]
        )
        obf_messages_by_cls = build_message_lookup(
            [
                DumpCSMessage(file_descriptor="obf_x", name="obf_x1", fields=[]),
                DumpCSMessage(file_descriptor="obf_x", name="obf_x2", fields=[]),
                DumpCSMessage(file_descriptor="obf_y", name="obf_y1", fields=[]),
            ]
        )
        non_obf_messages_by_cls = build_message_lookup(
            [
                DumpCSMessage(file_descriptor="group_a", name="clear_a1", fields=[]),
                DumpCSMessage(file_descriptor="group_a", name="clear_a2", fields=[]),
                DumpCSMessage(file_descriptor="group_b", name="clear_b1", fields=[]),
            ]
        )

        matches = select_grouped_matches_for_test(
            workspace=workspace,
            prepared_scores=PreparedScoreData(
                final_scores_matrix=final_scores_matrix,
                candidate_eligibility_mask=np.ones_like(final_scores_matrix, dtype=bool),
                structure_scores_matrix=np.array(
                    [
                        [0.90, 0.10, 0.40],
                        [0.20, 0.89, 0.10],
                        [0.30, 0.31, 0.85],
                    ]
                ),
                assembly_scores_matrix=np.array(
                    [
                        [0.70, 0.10, 0.95],
                        [0.10, 0.69, 0.10],
                        [0.30, 0.31, 0.60],
                    ]
                ),
                runtime_confidence_by_pair={},
                file_descriptor_similarity_by_pair={
                    ("group_a", "obf_x"): 0.795,
                    ("group_b", "obf_y"): 0.6,
                },
            ),
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )
        matched_obf_by_non_obf = {
            match.non_obf_signature.message_cls: match.obf_signature.message_cls for match in matches
        }

        assert matched_obf_by_non_obf == {
            "clear_a1": "obf_x1",
            "clear_a2": "obf_x2",
            "clear_b1": "obf_y1",
        }
        scores_by_non_obf = {
            match.non_obf_signature.message_cls: (
                match.group_similarity_score,
                match.assembly_similarity_score,
                match.structure_similarity_score,
            )
            for match in matches
        }
        assert scores_by_non_obf == {
            "clear_a1": (0.795, 0.7, 0.9),
            "clear_a2": (0.795, 0.69, 0.89),
            "clear_b1": (0.6, 0.6, 0.85),
        }

    def test_select_grouped_matches_processes_all_pinned_pairs_for_shared_obf_group(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_signatures = [
            message_signature("izm", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "iyb"}
            ),
            message_signature("iyw", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "iyb"}
            ),
            message_signature("iyr", declared_field_signatures=[]).model_copy(
                update={"file_descriptor": "iyb"}
            ),
        ]
        non_obf_signatures = [
            message_signature(
                "Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightSynchronizeEvent",
                declared_field_signatures=[],
            ).model_copy(update={"file_descriptor": "FightReflection"}),
            message_signature(
                "Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightTurnReadyRequest",
                declared_field_signatures=[],
            ).model_copy(update={"file_descriptor": "FightReflection"}),
            message_signature(
                "Com.Ankama.Dofus.Server.Game.Protocol.Character.CharacterCharacteristicsEvent",
                declared_field_signatures=[],
            ).model_copy(update={"file_descriptor": "CharacterReflection"}),
        ]
        workspace = build_matching_workspace(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )
        obf_messages_by_cls = build_message_lookup(
            [
                DumpCSMessage(file_descriptor="iyb", name="izm", fields=[]),
                DumpCSMessage(file_descriptor="iyb", name="iyw", fields=[]),
                DumpCSMessage(file_descriptor="iyb", name="iyr", fields=[]),
            ]
        )
        non_obf_messages_by_cls = build_message_lookup(
            [
                DumpCSMessage(
                    file_descriptor="FightReflection",
                    namespace="Com.Ankama.Dofus.Server.Game.Protocol.Fight",
                    name="FightSynchronizeEvent",
                    fields=[],
                ),
                DumpCSMessage(
                    file_descriptor="FightReflection",
                    namespace="Com.Ankama.Dofus.Server.Game.Protocol.Fight",
                    name="FightTurnReadyRequest",
                    fields=[],
                ),
                DumpCSMessage(
                    file_descriptor="CharacterReflection",
                    namespace="Com.Ankama.Dofus.Server.Game.Protocol.Character",
                    name="CharacterCharacteristicsEvent",
                    fields=[],
                ),
            ]
        )

        matches = select_grouped_matches_for_test(
            workspace=workspace,
            prepared_scores=PreparedScoreData(
                final_scores_matrix=np.array(
                    [
                        [1.0, 0.0, 0.0],
                        [0.0, 1.0, 0.0],
                        [0.0, 0.0, 1.0],
                    ]
                ),
                structure_scores_matrix=np.zeros((3, 3)),
                candidate_eligibility_mask=np.ones((3, 3), dtype=bool),
                assembly_scores_matrix=np.zeros((3, 3)),
                runtime_confidence_by_pair={},
                file_descriptor_similarity_by_pair={
                    ("FightReflection", "iyb"): 1.0,
                    ("CharacterReflection", "iyb"): 1.0,
                },
            ),
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=PinnedPairsConfig(
                pairs=[
                    PinnedPair(
                        obf="izm",
                        non_obf="Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightSynchronizeEvent",
                    ),
                    PinnedPair(
                        obf="iyw",
                        non_obf="Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightTurnReadyRequest",
                    ),
                    PinnedPair(
                        obf="iyr",
                        non_obf=(
                            "Com.Ankama.Dofus.Server.Game.Protocol.Character.CharacterCharacteristicsEvent"
                        ),
                    ),
                ]
            ),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )
        matched_obf_by_non_obf = {
            match.non_obf_signature.message_cls: match.obf_signature.message_cls for match in matches
        }

        assert matched_obf_by_non_obf == {
            "Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightSynchronizeEvent": "izm",
            "Com.Ankama.Dofus.Server.Game.Protocol.Fight.FightTurnReadyRequest": "iyw",
            "Com.Ankama.Dofus.Server.Game.Protocol.Character.CharacterCharacteristicsEvent": "iyr",
        }
        assert len(matches) == 3

    def test_child_discovery_from_field_mapping_improves_following_group_match(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_root = DumpCSMessage(
            file_descriptor="group_root",
            name="MapComplementaryInformationEvent",
            fields=[
                typed_dump_field(
                    field_name="stated_element_",
                    property_name="StatedElement",
                    normalized_type="StatedElement",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        obf_root = DumpCSMessage(
            file_descriptor="group_obf_root",
            name="isu",
            fields=[
                typed_dump_field(
                    field_name="a",
                    property_name="Faaa",
                    normalized_type="obf_state",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        non_obf_child = DumpCSMessage(
            file_descriptor="group_child",
            name="StatedElement",
            fields=[
                typed_dump_field(
                    field_name="element_id_",
                    property_name="ElementId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        wrong_non_obf_child = DumpCSMessage(
            file_descriptor="group_child",
            name="OtherElement",
            fields=[
                typed_dump_field(
                    field_name="other_id_",
                    property_name="OtherId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_child = DumpCSMessage(
            file_descriptor="group_obf_child",
            name="obf_state",
            fields=[
                typed_dump_field(
                    field_name="b",
                    property_name="Fbbb",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        wrong_obf_child = DumpCSMessage(
            file_descriptor="group_obf_child",
            name="wrong_obf_state",
            fields=[
                typed_dump_field(
                    field_name="c",
                    property_name="Fccc",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        non_obf_signatures = [
            message_signature(
                "MapComplementaryInformationEvent",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "stated_element_")}),
                dump_cs_msg=non_obf_root,
            ),
            message_signature(
                "StatedElement",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "element_id_")}),
                dump_cs_msg=non_obf_child,
            ),
            message_signature(
                "OtherElement",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "other_id_")}),
                dump_cs_msg=wrong_non_obf_child,
            ),
        ]
        obf_signatures = [
            message_signature(
                "isu",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "a")}),
                dump_cs_msg=obf_root,
            ),
            message_signature(
                "obf_state",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "b")}),
                dump_cs_msg=obf_child,
            ),
            message_signature(
                "wrong_obf_state",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "c")}),
                dump_cs_msg=wrong_obf_child,
            ),
        ]
        workspace = build_matching_workspace(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child, wrong_obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child, wrong_non_obf_child]),
        )

        matches = select_grouped_matches_for_test(
            workspace=workspace,
            prepared_scores=PreparedScoreData(
                final_scores_matrix=np.array(
                    [
                        [0.92, 0.0, 0.0],
                        [0.0, 0.70, 0.74],
                        [0.0, 0.40, 0.30],
                    ]
                ),
                structure_scores_matrix=np.array(
                    [
                        [0.92, 0.0, 0.0],
                        [0.0, 0.70, 0.74],
                        [0.0, 0.40, 0.30],
                    ]
                ),
                candidate_eligibility_mask=np.ones((3, 3), dtype=bool),
                assembly_scores_matrix=np.array(
                    [
                        [0.92, 0.0, 0.0],
                        [0.0, 0.70, 0.74],
                        [0.0, 0.40, 0.30],
                    ]
                ),
                runtime_confidence_by_pair={},
                file_descriptor_similarity_by_pair={
                    ("group_root", "group_obf_root"): 1.0,
                    ("group_child", "group_obf_child"): 1.0,
                },
            ),
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child, wrong_obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child, wrong_non_obf_child]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )

        matched_obf_by_non_obf = {
            match.non_obf_signature.message_cls: match.obf_signature.message_cls for match in matches
        }

        assert matched_obf_by_non_obf["MapComplementaryInformationEvent"] == "isu"
        assert matched_obf_by_non_obf["StatedElement"] == "obf_state"

    @pytest.mark.parametrize("child_eligible", [True, False])
    def test_child_discovery_from_field_mapping_emits_only_eligible_zero_score_child(
        self, runtime_data_store: RuntimeDataStore, child_eligible: bool
    ) -> None:
        non_obf_root = DumpCSMessage(
            file_descriptor="group_root",
            name="MapComplementaryInformationEvent",
            fields=[
                typed_dump_field(
                    field_name="stated_element_",
                    property_name="StatedElement",
                    normalized_type="StatedElement",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        obf_root = DumpCSMessage(
            file_descriptor="group_obf_root",
            name="isu",
            fields=[
                typed_dump_field(
                    field_name="state_obf",
                    property_name="StateObf",
                    normalized_type="obf_state",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        non_obf_child = DumpCSMessage(
            file_descriptor="group_child",
            name="StatedElement",
            fields=[
                typed_dump_field(
                    field_name="element_id_",
                    property_name="ElementId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_child = DumpCSMessage(
            file_descriptor="group_obf_child",
            name="obf_state",
            fields=[
                typed_dump_field(
                    field_name="element_obf",
                    property_name="ElementObf",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        non_obf_signatures = [
            message_signature(
                "MapComplementaryInformationEvent",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "stated_element_")}),
                dump_cs_msg=non_obf_root,
            ),
            message_signature(
                "StatedElement",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "element_id_")}),
                dump_cs_msg=non_obf_child,
            ),
        ]
        obf_signatures = [
            message_signature(
                "isu",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "state_obf")}),
                dump_cs_msg=obf_root,
            ),
            message_signature(
                "obf_state",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "element_obf")}),
                dump_cs_msg=obf_child,
            ),
        ]
        workspace = build_matching_workspace(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child]),
        )

        matches = select_grouped_matches_for_test(
            workspace=workspace,
            prepared_scores=PreparedScoreData(
                final_scores_matrix=np.array(
                    [
                        [0.92, 0.0],
                        [0.0, 0.0],
                    ]
                ),
                structure_scores_matrix=np.array(
                    [
                        [0.92, 0.0],
                        [0.0, 0.0],
                    ]
                ),
                candidate_eligibility_mask=np.array([[True, True], [True, child_eligible]]),
                assembly_scores_matrix=np.array(
                    [
                        [0.92, 0.0],
                        [0.0, 0.0],
                    ]
                ),
                runtime_confidence_by_pair={},
                file_descriptor_similarity_by_pair={
                    ("group_root", "group_obf_root"): 1.0,
                    ("group_child", "group_obf_child"): 1.0,
                },
            ),
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )
        matched_obf_by_non_obf = {
            match.non_obf_signature.message_cls: match.obf_signature.message_cls for match in matches
        }

        expected = {"MapComplementaryInformationEvent": "isu"}
        if child_eligible:
            expected["StatedElement"] = "obf_state"
        assert matched_obf_by_non_obf == expected

    def test_select_grouped_matches_returns_pair_specific_scores(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_x1 = DumpCSMessage(file_descriptor="obf_x", name="obf_x1", fields=[])
        obf_x2 = DumpCSMessage(
            file_descriptor="obf_x",
            name="obf_x2",
            fields=[
                typed_dump_field(
                    field_name="b",
                    property_name="B",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_y1 = DumpCSMessage(file_descriptor="obf_y", name="obf_y1", fields=[])
        clear_a1 = DumpCSMessage(file_descriptor="group_a", name="clear_a1", fields=[])
        clear_a2 = DumpCSMessage(
            file_descriptor="group_a",
            name="clear_a2",
            fields=[
                typed_dump_field(
                    field_name="cell_id_",
                    property_name="CellId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        clear_b1 = DumpCSMessage(file_descriptor="group_b", name="clear_b1", fields=[])
        obf_signatures = [
            message_signature("obf_x1", declared_field_signatures=[], dump_cs_msg=obf_x1).model_copy(
                update={"file_descriptor": "obf_x"}
            ),
            message_signature(
                "obf_x2",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "b")}),
                dump_cs_msg=obf_x2,
            ).model_copy(update={"file_descriptor": "obf_x"}),
            message_signature("obf_y1", declared_field_signatures=[], dump_cs_msg=obf_y1).model_copy(
                update={"file_descriptor": "obf_y"}
            ),
        ]
        non_obf_signatures = [
            message_signature("clear_a1", declared_field_signatures=[], dump_cs_msg=clear_a1).model_copy(
                update={"file_descriptor": "group_a"}
            ),
            message_signature(
                "clear_a2",
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                live_field_keys=frozenset({FieldKey(0x18, "cell_id_")}),
                dump_cs_msg=clear_a2,
            ).model_copy(update={"file_descriptor": "group_a"}),
            message_signature("clear_b1", declared_field_signatures=[], dump_cs_msg=clear_b1).model_copy(
                update={"file_descriptor": "group_b"}
            ),
        ]
        workspace = build_matching_workspace(
            obf_signatures=obf_signatures,
            non_obf_signatures=non_obf_signatures,
            obf_messages_by_cls={},
            non_obf_messages_by_cls={},
        )
        prepared_scores = PreparedScoreData(
            candidate_eligibility_mask=np.ones((3, 3), dtype=bool),
            final_scores_matrix=np.array(
                [
                    [0.80, 0.10, 0.20],
                    [0.10, 0.79, 0.10],
                    [0.30, 0.31, 0.60],
                ]
            ),
            structure_scores_matrix=np.array(
                [
                    [0.90, 0.10, 0.40],
                    [0.20, 0.89, 0.10],
                    [0.30, 0.31, 0.85],
                ]
            ),
            assembly_scores_matrix=np.array(
                [
                    [0.70, 0.10, 0.95],
                    [0.10, 0.69, 0.10],
                    [0.30, 0.31, 0.60],
                ]
            ),
            runtime_confidence_by_pair={MatchPairKey("obf_x2", "clear_a2"): 0.42},
            file_descriptor_similarity_by_pair={
                ("group_a", "obf_x"): 0.795,
                ("group_b", "obf_y"): 0.6,
            },
        )

        matches = select_grouped_matches_for_test(
            workspace=workspace,
            prepared_scores=prepared_scores,
            obf_messages_by_cls=build_message_lookup([obf_x1, obf_x2, obf_y1]),
            non_obf_messages_by_cls=build_message_lookup([clear_a1, clear_a2, clear_b1]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
        )
        result = next(match for match in matches if match.non_obf_signature.message_cls == "clear_a2")

        assert result.non_obf_signature == non_obf_signatures[1]
        assert result.obf_signature == obf_signatures[1]
        assert result.score == 0.79
        assert result.group_similarity_score == 0.795
        assert result.assembly_similarity_score == 0.69
        assert result.structure_similarity_score == 0.89
        assert result.field_mapping == {"b": "cell_id"}
        assert result.runtime_confidence == 0.42
