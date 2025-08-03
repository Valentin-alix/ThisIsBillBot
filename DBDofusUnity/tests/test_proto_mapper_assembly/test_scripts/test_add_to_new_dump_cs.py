from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.field_builders import dump_cs_field

from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.tests.test_proto_mapper_assembly.fixture.script_builders import game_mapping_entry
from proto_mapper_assembly.interfaces.game_mappings import GameMappingsDocument
from proto_mapper_assembly.scripts import add_to_new_dump_cs
from proto_mapper_assembly.scripts.add_to_new_dump_cs import (
    _preserve_existing_field_offsets,
    build_new_dump_cs_entries,
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
