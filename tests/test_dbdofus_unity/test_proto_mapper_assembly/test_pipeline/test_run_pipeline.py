from pathlib import Path
from unittest.mock import ANY, patch

from tests.fixtures.proto_mapper.message_builders import message_signature
from tests.fixtures.proto_mapper.pipeline_builders import (
    builder_matching_inputs,
    simple_match_result,
)

from DBDofusUnity.consts import (
    AUTO_MODE_MAPPING_CONTRACT_FILE,
    CAPTURE_SEQUENCE_HINTS_FILE,
    GAME_MAPPINGS_DETAILED_JSON_FILE,
    GAME_MAPPINGS_JSON_FILE,
    NON_OBF_NEW_DUMP_CS_FILE,
    NON_OBF_PROTO_ACCESSES_FILE,
    NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from DBDofusUnity.proto_mapper_assembly.pipeline import run_pipeline


class TestRunPipeline:
    def test_writes_game_mappings_from_direct_match_results(self) -> None:
        clear_b = message_signature("ClearB", declared_field_signatures=[])
        clear_a = message_signature("ClearA", declared_field_signatures=[])
        obf_b = message_signature("obf_b", declared_field_signatures=[])
        obf_a = message_signature("obf_a", declared_field_signatures=[])
        obf_messages_by_cls = {
            "obf_b": DumpCSMessage(file_descriptor="GameReflection", name="obf_b"),
            "obf_a": DumpCSMessage(file_descriptor="GameReflection", name="obf_a"),
        }
        non_obf_messages_by_cls = {
            "ClearB": DumpCSMessage(file_descriptor="GameReflection", name="ClearB"),
            "ClearA": DumpCSMessage(file_descriptor="GameReflection", name="ClearA"),
        }
        matches = (
            simple_match_result(non_obf_cls="ClearB", obf_cls="obf_b", score=0.2),
            simple_match_result(non_obf_cls="ClearA", obf_cls="obf_a", score=0.9),
        )
        fake_pinned = PinnedPairsConfig(pairs=[PinnedPair(obf="kmv", non_obf="Com.Ankama.Common.Message")])
        fake_hints = CaptureSequenceHintsConfig(sequences=())

        with (
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_matching_inputs",
                return_value=builder_matching_inputs(
                    obf_messages_by_cls=obf_messages_by_cls,
                    non_obf_messages_by_cls=non_obf_messages_by_cls,
                    obf_signatures_by_cls={"obf_b": obf_b, "obf_a": obf_a},
                    non_obf_signatures_by_cls={"ClearB": clear_b, "ClearA": clear_a},
                ),
            ),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.load_pinned_pairs", return_value=fake_pinned),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_pinned_pairs_non_obf_targets",
                return_value=fake_pinned,
            ),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_new_dump_cs_messages",
                return_value=NewDumpCSFile(root={}),
            ),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_capture_sequence_hints", return_value=fake_hints
            ) as mock_load_hints,
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_capture_sequence_hints_non_obf_targets",
                return_value=fake_hints,
            ),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.match_messages", return_value=matches) as mock_match,
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.write_game_mappings") as mock_write_game_mappings,
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.check_auto_mode_mappings"),
        ):
            run_pipeline(do_load_pinned_pair=True)

        mock_match.assert_called_once()
        mock_load_hints.assert_called_once_with(CAPTURE_SEQUENCE_HINTS_FILE)
        mock_write_game_mappings.assert_called_once_with(
            matches,
            obf_messages_by_cls=obf_messages_by_cls,
            non_obf_messages_by_cls=non_obf_messages_by_cls,
            output_path=GAME_MAPPINGS_JSON_FILE,
            detailed_output_path=GAME_MAPPINGS_DETAILED_JSON_FILE,
        )

    def test_resolves_pinned_pairs_against_dump_and_manual_new_dump_cs_messages(self) -> None:
        obf_message = DumpCSMessage(file_descriptor="gamemap_reflection", name="irk")
        dump_non_obf_message = DumpCSMessage(
            file_descriptor="gamemap_reflection",
            name="SomeExistingMsg",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Gamemap",
        )
        manual_non_obf_message = DumpCSMessage(
            file_descriptor="gamemap_reflection",
            name="MapMovementConfirmResponse",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Gamemap",
        )
        fake_pinned = PinnedPairsConfig(pairs=[PinnedPair(obf="irk", non_obf="MapMovementConfirmResponse")])
        fake_hints = CaptureSequenceHintsConfig(sequences=())

        with (
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_matching_inputs",
                return_value=builder_matching_inputs(
                    obf_messages_by_cls={"irk": obf_message},
                    non_obf_messages_by_cls={dump_non_obf_message.composed_name: dump_non_obf_message},
                    obf_signatures_by_cls={"irk": message_signature("irk", declared_field_signatures=[])},
                    non_obf_signatures_by_cls={},
                ),
            ),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.load_pinned_pairs", return_value=fake_pinned),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_new_dump_cs_messages",
                return_value=NewDumpCSFile(
                    root={manual_non_obf_message.composed_name: manual_non_obf_message}
                ),
            ),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_pinned_pairs_non_obf_targets",
                return_value=fake_pinned,
            ) as mock_resolve_pinned_pairs,
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.load_capture_sequence_hints", return_value=fake_hints),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_capture_sequence_hints_non_obf_targets",
                return_value=fake_hints,
            ),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.match_messages", return_value=()),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.write_game_mappings"),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.check_auto_mode_mappings"),
        ):
            run_pipeline(do_load_pinned_pair=True)

        mock_resolve_pinned_pairs.assert_called_once_with(
            pinned_pairs=fake_pinned,
            obf_messages_by_cls={"irk": obf_message},
            non_obf_messages_by_cls={
                dump_non_obf_message.composed_name: dump_non_obf_message,
                manual_non_obf_message.composed_name: manual_non_obf_message,
            },
        )

    def test_uses_obf_dir_for_inputs_pins_overrides_and_outputs(self, tmp_path: Path) -> None:
        obf_dir = tmp_path / "20_05_2026"
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="obf")
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="Clear")
        fake_pinned = PinnedPairsConfig(pairs=[PinnedPair(obf="obf", non_obf="Clear")])
        matches = (simple_match_result(non_obf_cls="Clear", obf_cls="obf", score=0.9),)
        fake_hints = CaptureSequenceHintsConfig(sequences=())

        with (
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_matching_inputs",
                return_value=builder_matching_inputs(
                    obf_messages_by_cls={"obf": obf_message},
                    non_obf_messages_by_cls={"Clear": non_obf_message},
                    obf_signatures_by_cls={"obf": message_signature("obf", declared_field_signatures=[])},
                    non_obf_signatures_by_cls={
                        "Clear": message_signature("Clear", declared_field_signatures=[])
                    },
                ),
            ) as mock_load_matching_inputs,
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_pinned_pairs", return_value=fake_pinned
            ) as mock_load_pinned_pairs,
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_pinned_pairs_non_obf_targets",
                return_value=fake_pinned,
            ),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.load_new_dump_cs_messages",
                return_value=NewDumpCSFile(root={}),
            ) as mock_load_new_dump_cs_messages,
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.load_capture_sequence_hints", return_value=fake_hints),
            patch(
                "DBDofusUnity.proto_mapper_assembly.pipeline.resolve_capture_sequence_hints_non_obf_targets",
                return_value=fake_hints,
            ),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.match_messages", return_value=matches),
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.write_game_mappings") as mock_write_game_mappings,
            patch("DBDofusUnity.proto_mapper_assembly.pipeline.check_auto_mode_mappings") as mock_check_auto_mode_mappings,
        ):
            run_pipeline(do_load_pinned_pair=True, obf_dir=obf_dir)

        mock_load_matching_inputs.assert_called_once_with(
            obf_dump_cs_path=obf_dir / "cs" / "Ankama.Dofus.Protocol.Game.cs",
            non_obf_dump_cs_path=NON_OBF_PROTOCOL_GAME_DUMP_CS_FILE,
            obf_proto_accesses_path=obf_dir / "proto_accesses.json",
            non_obf_proto_accesses_path=NON_OBF_PROTO_ACCESSES_FILE,
            bootstrap_non_obf_dump_cs_path=NON_OBF_NEW_DUMP_CS_FILE,
            signature_overrides_path=obf_dir / "messages_access_signature_override.json",
        )
        mock_load_new_dump_cs_messages.assert_called_once_with(NON_OBF_NEW_DUMP_CS_FILE)
        mock_load_pinned_pairs.assert_called_once_with(obf_dir / "pinned_pairs.json")
        mock_write_game_mappings.assert_called_once_with(
            matches,
            obf_messages_by_cls={"obf": obf_message},
            non_obf_messages_by_cls={"Clear": non_obf_message},
            output_path=obf_dir / "game_mappings.json",
            detailed_output_path=obf_dir / "game_mappings_detailed.json",
        )
        mock_check_auto_mode_mappings.assert_called_once_with(
            contract_path=AUTO_MODE_MAPPING_CONTRACT_FILE,
            detailed_mappings_path=obf_dir / "game_mappings_detailed.json",
            pinned_pairs_path=obf_dir / "pinned_pairs.json",
            observed_root_obf_messages=ANY,
        )
