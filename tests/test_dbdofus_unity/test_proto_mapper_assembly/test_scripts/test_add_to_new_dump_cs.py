from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import dump_cs_field

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from proto_mapper_assembly.interfaces.excluded_non_obf import ExcludedNonObfConfig
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.script_builders import game_mapping_entry
from proto_mapper_assembly.interfaces.game_mappings import (
    GameMappingsDocument,
    SimpleGameMappingEntry,
    SimpleGameMappingsDocument,
)
from proto_mapper_assembly.scripts import add_to_new_dump_cs
from proto_mapper_assembly.scripts.add_to_new_dump_cs import (
    _preserve_existing_field_offsets,
    build_new_dump_cs_entries,
    rebuild_new_dump_cs_from_protobufs,
    synchronize_non_obf_mapping_artifacts,
)
from proto_mapper_assembly.interfaces.new_dump_cs import NewDumpCSFile
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair, PinnedPairsConfig
from proto_mapper_assembly.interfaces.signature_overrides import (
    SignatureOverrideEntry,
    SignatureOverridesFile,
)


class TestPreserveExistingFieldOffsets:
    def test_copies_existing_offsets_and_keeps_new_fields_at_zero(self) -> None:
        existing_actor_id = dump_cs_field("int", offset=0x18, field_name="actorId_").model_copy(
            update={"property_name": "ActorId"}
        )
        existing_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ActorEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Actor",
            fields=[
                existing_actor_id,
                dump_cs_field("string", offset=0x20, field_name="unrelated_").model_copy(
                    update={"property_name": "Unrelated"}
                ),
            ],
        )
        generated_message = existing_message.model_copy(
            update={
                "fields": [
                    dump_cs_field("int", offset=0, field_name="actorId_").model_copy(
                        update={"property_name": "ActorId", "proto_decl_order": 1}
                    ),
                    dump_cs_field("long", offset=0, field_name="newValue_").model_copy(
                        update={"property_name": "NewValue", "proto_decl_order": 2}
                    ),
                ]
            }
        )

        result = _preserve_existing_field_offsets(generated_message, existing_message)

        assert [field.memory_offset for field in result.fields] == [0x18, 0]
        assert [field.property_name for field in result.fields] == ["ActorId", "NewValue"]

    def test_returns_generated_message_when_no_existing_message_is_available(self) -> None:
        generated_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="NewEvent",
            fields=[dump_cs_field("int", offset=0, field_name="value_")],
        )

        result = _preserve_existing_field_offsets(generated_message, None)

        assert result is generated_message


class TestBuildNewDumpCsEntries:
    def test_writes_entries_and_preserves_existing_offsets(self) -> None:
        existing_field = dump_cs_field("int", offset=0x18, field_name="actorId_").model_copy(
            update={"property_name": "ActorId"}
        )
        existing_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ActorEvent",
            namespace="Com.Ankama",
            fields=[existing_field],
        )
        generated_message = existing_message.model_copy(
            update={
                "fields": [
                    dump_cs_field("int", offset=0, field_name="actorId_").model_copy(
                        update={"property_name": "ActorId"}
                    )
                ]
            }
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            non_obf_dump_cs_path = Path(temp_dir) / "dump.cs"
            non_obf_dump_cs_path.write_text("", encoding="utf-8")
            new_dump_cs_path = Path(temp_dir) / "new_dump_cs.json"

            with (
                patch(
                    "proto_mapper_assembly.scripts.add_to_new_dump_cs.build_dump_cs_messages_from_pb2",
                    return_value={"Com.Ankama.ActorEvent": generated_message},
                ),
                patch(
                    "proto_mapper_assembly.scripts.add_to_new_dump_cs.parse_messages",
                    return_value=[existing_message],
                ),
            ):
                result = build_new_dump_cs_entries(
                    ["Com.Ankama.ActorEvent"],
                    protos_dir=Path("unused"),
                    non_obf_dump_cs_path=non_obf_dump_cs_path,
                    new_dump_cs_path=new_dump_cs_path,
                )

            assert result.root["Com.Ankama.ActorEvent"].fields[0].memory_offset == 0x18
            written = json.loads(new_dump_cs_path.read_text(encoding="utf-8"))
            assert "Com.Ankama.ActorEvent" in written


class TestSynchronizeNonObfMappingArtifacts:
    def test_rebuilds_exclusions_and_prunes_orphaned_mapping_artifacts(self, tmp_path: Path) -> None:
        live_message = DumpCSMessage(
            file_descriptor="LiveReflection",
            name="LiveEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Live",
        )
        stale_message = DumpCSMessage(
            file_descriptor="StaleReflection",
            name="StaleEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Stale",
        )
        live_name = live_message.composed_name
        stale_name = stale_message.composed_name
        new_dump_path = tmp_path / "new_dump_cs.json"
        excluded_path = tmp_path / "excluded_non_obf.json"
        pins_path = tmp_path / "pinned_pairs.json"
        overrides_path = tmp_path / "overrides.json"
        mappings_path = tmp_path / "game_mappings.json"
        detailed_mappings_path = tmp_path / "game_mappings_detailed.json"
        new_dump_path.write_text(
            NewDumpCSFile(root={live_name: live_message, stale_name: stale_message}).model_dump_json(),
            encoding="utf-8",
        )
        pins_path.write_text(
            PinnedPairsConfig(
                pairs=[PinnedPair(obf="live", non_obf=live_name), PinnedPair(obf="stale", non_obf=stale_name)]
            ).model_dump_json(),
            encoding="utf-8",
        )
        empty_override = SignatureOverrideEntry(function_signatures=[], field_signatures={})
        overrides_path.write_text(
            SignatureOverridesFile(
                root={live_name: empty_override, stale_name: empty_override}
            ).model_dump_json(),
            encoding="utf-8",
        )
        live_mapping_key = ".com.ankama.dofus.server.game.protocol.live.LiveEvent"
        stale_mapping_key = ".com.ankama.dofus.server.game.protocol.stale.StaleEvent"
        mappings_path.write_text(
            SimpleGameMappingsDocument(
                root={
                    live_mapping_key: SimpleGameMappingEntry(obf_msg_namespace="live", field_mapping={}),
                    stale_mapping_key: SimpleGameMappingEntry(obf_msg_namespace="stale", field_mapping={}),
                }
            ).model_dump_json(),
            encoding="utf-8",
        )
        detailed_mappings_path.write_text(
            GameMappingsDocument(
                root={
                    live_mapping_key: game_mapping_entry(
                        field_mapping={}, obf_cls="live", non_obf_namespace=live_mapping_key
                    ),
                    stale_mapping_key: game_mapping_entry(
                        field_mapping={}, obf_cls="stale", non_obf_namespace=stale_mapping_key
                    ),
                }
            ).model_dump_json(),
            encoding="utf-8",
        )

        with (
            patch(
                "proto_mapper_assembly.scripts.add_to_new_dump_cs.build_dump_cs_messages_from_pb2",
                return_value={live_name: live_message},
            ),
            patch(
                "proto_mapper_assembly.scripts.add_to_new_dump_cs.parse_messages",
                return_value=[live_message, stale_message],
            ),
        ):
            synchronize_non_obf_mapping_artifacts(
                protos_dir=tmp_path,
                non_obf_dump_cs_path=tmp_path / "Ankama.Dofus.Protocol.Game.cs",
                new_dump_cs_path=new_dump_path,
                excluded_non_obf_path=excluded_path,
                pinned_pairs_path=pins_path,
                signature_overrides_path=overrides_path,
                game_mappings_path=mappings_path,
                game_mappings_detailed_path=detailed_mappings_path,
            )

        assert set(NewDumpCSFile.model_validate_json(new_dump_path.read_text()).root) == {live_name}
        assert [
            pair.non_obf for pair in PinnedPairsConfig.model_validate_json(pins_path.read_text()).pairs
        ] == [live_name]
        assert set(SignatureOverridesFile.model_validate_json(overrides_path.read_text()).root) == {live_name}
        exclusion_document = ExcludedNonObfConfig.model_validate_json(excluded_path.read_text())
        assert exclusion_document.root == [stale_name]
        assert set(SimpleGameMappingsDocument.model_validate_json(mappings_path.read_text()).root) == {
            live_mapping_key
        }
        assert set(GameMappingsDocument.model_validate_json(detailed_mappings_path.read_text()).root) == {
            live_mapping_key
        }

    def test_retains_and_normalizes_nested_pinned_aliases(self, tmp_path: Path) -> None:
        root_message = DumpCSMessage(
            file_descriptor="OuterReflection",
            name="Outer",
            namespace="Com.Ankama",
            fields=[dump_cs_field("int", field_name="value_")],
        )
        nested_message = DumpCSMessage(
            file_descriptor="OuterReflection",
            name="Inner",
            namespace="Com.Ankama",
            parent_name="Outer.Types",
        )
        pins_path = tmp_path / "pinned_pairs.json"
        pins_path.write_text(
            PinnedPairsConfig(
                pairs=[PinnedPair(obf="xyz", non_obf="Com.Ankama.Outer.Inner")]
            ).model_dump_json(),
            encoding="utf-8",
        )

        add_to_new_dump_cs._prune_pinned_pairs(
            messages_by_cls={
                root_message.composed_name: root_message,
                nested_message.composed_name: nested_message,
            },
            path=pins_path,
        )

        retained_pairs = PinnedPairsConfig.model_validate_json(pins_path.read_text()).pairs

        assert [pair.non_obf for pair in retained_pairs] == ["Com.Ankama.Outer.Inner"]

    def test_rebuilds_every_protobuf_descriptor_and_retains_bootstrap_offsets(self, tmp_path: Path) -> None:
        first_message = DumpCSMessage(file_descriptor="FirstReflection", name="First")
        second_message = DumpCSMessage(file_descriptor="SecondReflection", name="Second")
        first_name = first_message.composed_name
        second_name = second_message.composed_name
        existing_field = dump_cs_field("int", offset=0x18, field_name="value_")
        generated_first = first_message.model_copy(
            update={"fields": [existing_field.model_copy(update={"memory_offset": 0})]}
        )
        generated_second = second_message.model_copy(
            update={"fields": [existing_field.model_copy(update={"memory_offset": 0})]}
        )
        bootstrap_second = second_message.model_copy(update={"fields": [existing_field]})
        new_dump_path = tmp_path / "new_dump_cs.json"
        new_dump_path.write_text(
            NewDumpCSFile(root={second_name: bootstrap_second}).model_dump_json(), encoding="utf-8"
        )

        with (
            patch(
                "proto_mapper_assembly.scripts.add_to_new_dump_cs.build_dump_cs_messages_from_pb2",
                return_value={first_name: generated_first, second_name: generated_second},
            ),
            patch("proto_mapper_assembly.scripts.add_to_new_dump_cs.parse_messages", return_value=[]),
        ):
            result = rebuild_new_dump_cs_from_protobufs(
                protos_dir=tmp_path,
                non_obf_dump_cs_path=tmp_path / "Ankama.Dofus.Protocol.Game.cs",
                new_dump_cs_path=new_dump_path,
            )

        assert set(result.root) == {first_name, second_name}
        assert result.root[first_name].fields[0].memory_offset == 0
        assert result.root[second_name].fields[0].memory_offset == 0x18

    def test_raises_when_class_name_has_no_pb2_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            non_obf_dump_cs_path = Path(temp_dir) / "dump.cs"
            non_obf_dump_cs_path.write_text("", encoding="utf-8")
            new_dump_cs_path = Path(temp_dir) / "new_dump_cs.json"

            with (
                patch(
                    "proto_mapper_assembly.scripts.add_to_new_dump_cs.build_dump_cs_messages_from_pb2",
                    return_value={},
                ),
                pytest.raises(SystemExit, match="No protobuf descriptor found"),
            ):
                build_new_dump_cs_entries(
                    ["Com.Ankama.Missing"],
                    protos_dir=Path("unused"),
                    non_obf_dump_cs_path=non_obf_dump_cs_path,
                    new_dump_cs_path=new_dump_cs_path,
                )


class TestNestingGuard:
    NESTED_OBF = "klm.klk"
    FLAT_OBF = "klm"

    def test_warns_when_a_flat_declaration_maps_to_a_nested_obfuscated_class(self, tmp_path: Path) -> None:
        """A root/nested disagreement makes build_static_score_data skip the pair outright.

        The message still looks mapped afterwards, so nothing surfaces the loss - hence the check at
        authoring time rather than three builds later.
        """
        mappings = tmp_path / "game_mappings_detailed.json"
        mappings.write_text(
            GameMappingsDocument(
                root={
                    ".com.ankama.dofus.server.game.protocol.common.UnknownKlk": game_mapping_entry(
                        field_mapping={},
                        obf_cls=self.NESTED_OBF,
                        non_obf_namespace=".com.ankama.dofus.server.game.protocol.common.UnknownKlk",
                    )
                }
            ).model_dump_json(),
            encoding="utf-8",
        )
        message = DumpCSMessage(
            file_descriptor="CommonReflection",
            name="UnknownKlk",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Common",
            fields=[],
            properties=[],
            parent_name=None,
        )

        warning = add_to_new_dump_cs.check_nesting_matches_obfuscated_side(
            message, game_mappings_path=mappings
        )

        assert warning is not None
        assert "klm.klk" in warning
        assert "Parent>.Types.UnknownKlk" in warning

    def test_stays_silent_when_the_obfuscated_class_is_top_level(self, tmp_path: Path) -> None:
        mappings = tmp_path / "game_mappings_detailed.json"
        mappings.write_text(
            GameMappingsDocument(
                root={
                    ".com.ankama.dofus.server.game.protocol.common.UnknownKlm": game_mapping_entry(
                        field_mapping={},
                        obf_cls=self.FLAT_OBF,
                        non_obf_namespace=".com.ankama.dofus.server.game.protocol.common.UnknownKlm",
                    )
                }
            ).model_dump_json(),
            encoding="utf-8",
        )
        message = DumpCSMessage(
            file_descriptor="CommonReflection",
            name="UnknownKlm",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Common",
            fields=[],
            properties=[],
            parent_name=None,
        )

        assert (
            add_to_new_dump_cs.check_nesting_matches_obfuscated_side(message, game_mappings_path=mappings)
            is None
        )
