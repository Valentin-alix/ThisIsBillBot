from pathlib import Path

import numpy as np
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.enum_builders import enum_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import (
    dump_field,
    enum_field,
    map_enum_field,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_field_mapping_for_test,
    build_message_lookup,
    build_verified_mapping,
    field_signature,
    make_field_mapping_context,
    message_signature,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_builders import runtime_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_store import seed_runtime_content
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import (
    ENUM_SHAPE,
    MESSAGE_SHAPE,
    NUMBER_SHAPE,
    REPEATED_MESSAGE_SHAPE,
    STRING_SHAPE,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import declared_field_signature

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.matching_builders import (
    match_messages_for_test,
)

from proto_mapper_assembly.field_mapping.field_mapping_scoring import score_field_pair
from proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from proto_mapper_assembly.interfaces.field_category import (
    FieldCategoryEnum,
    FieldTypeLeafKind,
    FieldTypeShape,
)
from proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from proto_mapper_assembly.interfaces.signature_overrides import (
    EnumSignatureOverrideHint,
    SignatureOverrideEntry,
)
from proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestMatchResultFieldMapping:
    def test_field_mapping_output_uses_canonical_proto_field_names(self) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SellingConditions",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Exchange",
            fields=[dump_field("types_", "Types_", 32, FieldCategoryEnum.REPEATED)],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="jfz",
            fields=[dump_field("fkkt", "fkkt", 32, FieldCategoryEnum.REPEATED)],
        )

        result = build_field_mapping_for_test(
            non_obf_signature=message_signature(
                "Com.Ankama.Dofus.Server.Game.Protocol.Exchange.SellingConditions",
                declared_field_signatures=[
                    declared_field_signature(FieldTypeShape(FieldCategoryEnum.REPEATED, None, None))
                ],
                field_signatures=[
                    field_signature(32, FieldTypeShape(FieldCategoryEnum.REPEATED, None, None))
                ],
                live_field_keys=frozenset({FieldKey(32, "types_")}),
                dump_cs_msg=non_obf_message,
            ),
            obf_signature=message_signature(
                "jfz",
                declared_field_signatures=[
                    declared_field_signature(FieldTypeShape(FieldCategoryEnum.REPEATED, None, None))
                ],
                field_signatures=[
                    field_signature(32, FieldTypeShape(FieldCategoryEnum.REPEATED, None, None))
                ],
                live_field_keys=frozenset({FieldKey(32, "fkkt")}),
                dump_cs_msg=obf_message,
            ),
            non_obf_messages_by_cls={
                "Com.Ankama.Dofus.Server.Game.Protocol.Exchange.SellingConditions": non_obf_message
            },
            obf_messages_by_cls={"jfz": obf_message},
            field_mapping_context=make_field_mapping_context(RuntimeDataStore()),
            pinned_pair=PinnedPair(
                obf="jfz",
                non_obf="Com.Ankama.Dofus.Server.Game.Protocol.Exchange.SellingConditions",
                field_mapping_by_obf={"fkkt": "types"},
            ),
        )

        assert result.field_mapping == {"fkkt": "types"}
        assert set(result.field_mapping_infos) == {"fkkt"}
        assert set(result.field_mapping_infos["fkkt"]) == {"types"}

    def test_accepts_pinned_field_without_observed_non_obf_access(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        sequence_type_field = dump_field("sequenceType_", "SequenceType", 0x18, FieldCategoryEnum.NUMBER)
        author_field = dump_field("authorId_", "AuthorId", 0x20, FieldCategoryEnum.NUMBER)
        obf_sequence_type_field = dump_field("efwq", "fifl", 0x18, FieldCategoryEnum.NUMBER)
        obf_author_field = dump_field("efwr", "fifm", 0x20, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="SequenceStartEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Game.Action",
            fields=[sequence_type_field, author_field],
        )
        obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="ium",
            fields=[obf_sequence_type_field, obf_author_field],
        )

        result = build_field_mapping_for_test(
            non_obf_signature=message_signature(
                non_obf_message.composed_name,
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(sequence_type_field.memory_offset, NUMBER_SHAPE)],
                live_field_keys=frozenset({sequence_type_field.field_key}),
                dump_cs_msg=non_obf_message,
            ),
            obf_signature=message_signature(
                obf_message.composed_name,
                declared_field_signatures=[
                    declared_field_signature(NUMBER_SHAPE),
                    declared_field_signature(NUMBER_SHAPE),
                ],
                field_signatures=[
                    field_signature(obf_sequence_type_field.memory_offset, NUMBER_SHAPE),
                    field_signature(obf_author_field.memory_offset, NUMBER_SHAPE),
                ],
                live_field_keys=frozenset({obf_sequence_type_field.field_key, obf_author_field.field_key}),
                dump_cs_msg=obf_message,
            ),
            non_obf_messages_by_cls={non_obf_message.composed_name: non_obf_message},
            obf_messages_by_cls={obf_message.composed_name: obf_message},
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            pinned_pair=PinnedPair(
                obf=obf_message.composed_name,
                non_obf=non_obf_message.composed_name,
                field_mapping_by_obf={"fifm": "author_id", "fifl": "sequence_type"},
            ),
        )

        assert result.field_mapping["fifm"] == "author_id"

    def test_prefers_runtime_alive_obf_field_over_equal_static_candidate(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_field = dump_field("target_id_", "TargetId", 0x18, FieldCategoryEnum.NUMBER)
        cold_obf_field = dump_field("cold_id_", "ColdId", 0x20, FieldCategoryEnum.NUMBER)
        runtime_obf_field = dump_field("runtime_id_", "RuntimeId", 0x20, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(file_descriptor="FD", name="TargetEvent", fields=[non_obf_field])
        obf_message = DumpCSMessage(
            file_descriptor="FD",
            name="obf_runtime_event",
            fields=[cold_obf_field, runtime_obf_field],
        )
        seed_runtime_content(tmp_path, {obf_message.composed_name: [{"runtime_id": 42}]})

        result = build_field_mapping_for_test(
            non_obf_signature=message_signature(
                non_obf_message.composed_name,
                declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                field_signatures=[field_signature(non_obf_field.memory_offset, NUMBER_SHAPE)],
                live_field_keys=frozenset({non_obf_field.field_key}),
                dump_cs_msg=non_obf_message,
            ),
            obf_signature=message_signature(
                obf_message.composed_name,
                declared_field_signatures=[
                    declared_field_signature(NUMBER_SHAPE),
                    declared_field_signature(NUMBER_SHAPE),
                ],
                field_signatures=[field_signature(cold_obf_field.memory_offset, NUMBER_SHAPE)],
                live_field_keys=frozenset({cold_obf_field.field_key}),
                dump_cs_msg=obf_message,
            ),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {"runtime_id": "target_id"}

    def test_score_pair_penalizes_bad_child_message_match(self, runtime_data_store: RuntimeDataStore) -> None:
        declared_field_signature(REPEATED_MESSAGE_SHAPE)
        non_obf_child = DumpCSMessage(file_descriptor="GameReflection", name="StatedElement")
        obf_child = DumpCSMessage(file_descriptor="GameReflection", name="kgp")
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapComplementaryInformationEvent",
            fields=[
                dump_field(
                    "stated_elements_",
                    "StatedElements",
                    24,
                    FieldCategoryEnum.REPEATED,
                    proto_decl_order=0,
                )
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.REPEATED)],
        )
        non_obf_message.fields[0].normalized_type = "RepeatedField<StatedElement>"
        non_obf_message.fields[0].clr_type = "RepeatedField<StatedElement>"
        obf_message.fields[0].normalized_type = "RepeatedField<kgp>"
        obf_message.fields[0].clr_type = "RepeatedField<kgp>"

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(24, REPEATED_MESSAGE_SHAPE),
            obf_access_signature=field_signature(24, REPEATED_MESSAGE_SHAPE),
            non_obf_field=non_obf_message.fields[0],
            obf_field=obf_message.fields[0],
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message, non_obf_child]),
            obf_messages_by_cls=build_message_lookup([obf_message, obf_child]),
            non_obf_type_index={"StatedElement": (non_obf_child,)},
            obf_type_index={"kgp": (obf_child,)},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(
                runtime_data_store,
                score_by_pair={
                    MatchPairKey("kgp", "StatedElement"): 0.05,
                },
            ),
            matching_store=None,
            pinned_pair=None,
        )

        assert score == 0.0
        assert metadata.child_message_score == 0.05

    def test_score_pair_rewards_good_child_message_match(self, runtime_data_store: RuntimeDataStore) -> None:
        declared_field_signature(REPEATED_MESSAGE_SHAPE)
        non_obf_child = DumpCSMessage(file_descriptor="GameReflection", name="StatedElement")
        obf_child = DumpCSMessage(file_descriptor="GameReflection", name="kgp")
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapComplementaryInformationEvent",
            fields=[
                dump_field(
                    "stated_elements_",
                    "StatedElements",
                    24,
                    FieldCategoryEnum.REPEATED,
                    proto_decl_order=0,
                )
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 32, FieldCategoryEnum.REPEATED)],
        )
        non_obf_message.fields[0].normalized_type = "RepeatedField<StatedElement>"
        non_obf_message.fields[0].clr_type = "RepeatedField<StatedElement>"
        obf_message.fields[0].normalized_type = "RepeatedField<kgp>"
        obf_message.fields[0].clr_type = "RepeatedField<kgp>"

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(24, REPEATED_MESSAGE_SHAPE),
            obf_access_signature=field_signature(32, REPEATED_MESSAGE_SHAPE),
            non_obf_field=non_obf_message.fields[0],
            obf_field=obf_message.fields[0],
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message, non_obf_child]),
            obf_messages_by_cls=build_message_lookup([obf_message, obf_child]),
            non_obf_type_index={"StatedElement": (non_obf_child,)},
            obf_type_index={"kgp": (obf_child,)},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(
                runtime_data_store,
                score_by_pair={
                    MatchPairKey("kgp", "StatedElement"): 0.9,
                },
            ),
            matching_store=None,
            pinned_pair=None,
        )

        assert score > 0.5
        assert metadata.child_match is not None

    def test_includes_field_mapping_from_runtime_and_declared_signatures(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="ChatChannelMessageRequest",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Chat",
            fields=[
                dump_field("content_", "Content", 24, FieldCategoryEnum.STRING, proto_decl_order=0),
                dump_field("channel_", "Channel", 32, FieldCategoryEnum.ENUM, proto_decl_order=1),
                dump_field("object_", "Object", 40, FieldCategoryEnum.REPEATED, proto_decl_order=2),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="jut",
            fields=[
                dump_field("elxf", "Flre", 24, FieldCategoryEnum.STRING),
                dump_field("elxh", "Flrf", 32, FieldCategoryEnum.ENUM),
                dump_field("elxk", "Flrg", 40, FieldCategoryEnum.REPEATED),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Chat.ChatChannelMessageRequest",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(REPEATED_MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, STRING_SHAPE),
                field_signature(32, ENUM_SHAPE),
                field_signature(40, REPEATED_MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset(
                {FieldKey(24, "content_"), FieldKey(32, "channel_"), FieldKey(40, "object_")}
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "jut",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(REPEATED_MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, STRING_SHAPE),
                field_signature(32, ENUM_SHAPE),
                field_signature(40, REPEATED_MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "elxf"), FieldKey(32, "elxh"), FieldKey(40, "elxk")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {
            "flre": "content",
            "flrf": "channel",
            "flrg": "object",
        }
        assert result.field_mapping_infos == {
            "flre": {"content": 1.0},
            "flrf": {"channel": 1.0},
            "flrg": {"object": 1.0},
        }

    def test_prefers_exact_verified_field_mapping_over_parent_verified_mapping(self) -> None:
        parent_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="GameActionFightEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Game.Action",
            fields=[dump_field("source_id_", "SourceId", 24, FieldCategoryEnum.NUMBER)],
        )
        child_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SpellRemove",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Game.Action",
            parent_name="GameActionFightEvent.Types",
            fields=[dump_field("target_id_", "TargetId", 24, FieldCategoryEnum.NUMBER)],
        )
        non_obf_signature = message_signature(
            "GameActionFightEvent.Types.SpellRemove",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "target_id_")}),
            dump_cs_msg=child_message,
        )
        obf_signature = message_signature(
            "ixc.SpellRemove",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "firs")}),
            dump_cs_msg=DumpCSMessage(
                file_descriptor="GameReflection",
                name="SpellRemove",
                namespace="ixc",
                parent_name="ixc",
                fields=[dump_field("firs", "Firs", 24, FieldCategoryEnum.NUMBER)],
            ),
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            non_obf_messages_by_cls={
                "Com.Ankama.Dofus.Server.Game.Protocol.Game.Action.GameActionFightEvent": parent_message,
                "GameActionFightEvent.Types.SpellRemove": child_message,
            },
            obf_messages_by_cls={"ixc.SpellRemove": obf_signature.dump_cs_msg},
            field_mapping_context=make_field_mapping_context(RuntimeDataStore()),
            pinned_pair=PinnedPair(
                obf="ixc.SpellRemove",
                non_obf="GameActionFightEvent.Types.SpellRemove",
                field_mapping_by_obf={"firs": "target_id"},
            ),
        )

        assert result.field_mapping == {"firs": "target_id"}

    def test_uses_child_type_resolution_for_child_discovery(self) -> None:
        nested_child_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SpellCast",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Game.Action",
            parent_name="TargetedAbility.Types",
            fields=[],
        )
        current_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="TargetedAbility",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Game.Action",
            parent_name="GameActionFightEvent.Types",
            fields=[dump_field("spell_cast_", "SpellCast", 24, FieldCategoryEnum.MESSAGE)],
        )
        current_message.fields[0].normalized_type = "SpellCast"
        current_message.fields[0].clr_type = "SpellCast"
        obf_nested_child_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="nsi",
            namespace="ixc",
            parent_name="ixc.iye",
            fields=[],
        )
        obf_current_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="iye",
            namespace="ixc",
            parent_name="ixc",
            fields=[dump_field("firo", "Firo", 24, FieldCategoryEnum.MESSAGE)],
        )
        obf_current_message.fields[0].normalized_type = "nsi"
        obf_current_message.fields[0].clr_type = "nsi"

        result = build_field_mapping_for_test(
            non_obf_signature=message_signature(
                "GameActionFightEvent.Types.TargetedAbility",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(24, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(24, "spell_cast_")}),
                dump_cs_msg=current_message,
            ),
            obf_signature=message_signature(
                "ixc.iye",
                declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                field_signatures=[field_signature(24, MESSAGE_SHAPE)],
                live_field_keys=frozenset({FieldKey(24, "firo")}),
                dump_cs_msg=obf_current_message,
            ),
            non_obf_messages_by_cls=build_message_lookup([current_message, nested_child_message]),
            obf_messages_by_cls=build_message_lookup([obf_current_message, obf_nested_child_message]),
            field_mapping_context=make_field_mapping_context(RuntimeDataStore()),
            non_obf_type_index={"SpellCast": (nested_child_message,)},
            obf_type_index={"nsi": (obf_nested_child_message,)},
        )

        assert result.field_mapping == {"firo": "spell_cast"}
        assert len(result.discovered_message_matches) == 1
        assert result.discovered_message_matches[0].obf_message_cls == "ixc.iye.nsi"
        assert result.discovered_message_matches[0].non_obf_message_cls == "TargetedAbility.Types.SpellCast"
        assert result.discovered_message_matches[0].reason == "field_mapping_child"

    def test_falls_back_to_declared_signatures_when_access_signatures_are_missing(self) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="Message",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Chat",
            fields=[
                dump_field("first_", "First", 24, FieldCategoryEnum.STRING, proto_decl_order=0),
                dump_field("second_", "Second", 32, FieldCategoryEnum.ENUM, proto_decl_order=1),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="abc",
            fields=[
                dump_field("e1", "Faaa", 24, FieldCategoryEnum.STRING),
                dump_field("e2", "Faab", 32, FieldCategoryEnum.ENUM),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Chat.Message",
            declared_field_signatures=[],
            dump_cs_msg=non_obf_message,
            live_field_keys=frozenset(field.field_key for field in non_obf_message.fields),
        )
        obf_signature = message_signature(
            "abc",
            declared_field_signatures=[],
            dump_cs_msg=obf_message,
            live_field_keys=frozenset(field.field_key for field in obf_message.fields),
        )

        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        assert result[0].field_mapping == {"faaa": "first", "faab": "second"}

    def test_skips_incompatible_declared_fields_in_fallback(self) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="Message",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Chat",
            fields=[
                dump_field("value_", "Value", 24, FieldCategoryEnum.STRING, proto_decl_order=0),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="abc",
            fields=[
                dump_field("e1", "Faaa", 24, FieldCategoryEnum.ENUM),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Chat.Message",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
            ],
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "abc",
            declared_field_signatures=[
                declared_field_signature(ENUM_SHAPE),
            ],
            dump_cs_msg=obf_message,
        )

        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        assert result == ()

    def test_maps_declared_obf_fields_without_live_access(self) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="Message",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Chat",
            fields=[
                dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field(
                    "instantiate_map_id_",
                    "InstantiateMapId",
                    32,
                    FieldCategoryEnum.NUMBER,
                    proto_decl_order=1,
                ),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="abc",
            fields=[
                dump_field("e1", "Fgvo", 24, FieldCategoryEnum.NUMBER),
                dump_field("e2", "Fgvp", 32, FieldCategoryEnum.NUMBER),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Chat.Message",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
            ],
            field_signatures=[
                field_signature(24, NUMBER_SHAPE),
                field_signature(32, NUMBER_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "map_id_"), FieldKey(32, "instantiate_map_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "abc",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
            ],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "e1")}),
            dump_cs_msg=obf_message,
        )

        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        assert len(result) == 1
        assert result[0].field_mapping == {
            "fgvo": "map_id",
            "fgvp": "instantiate_map_id",
        }

    def test_runtime_driven_mapping_does_not_depend_on_dump_field_order(self) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="Message",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Chat",
            fields=[
                dump_field("content_", "Content", 24, FieldCategoryEnum.STRING, proto_decl_order=0),
                dump_field("channel_", "Channel", 32, FieldCategoryEnum.ENUM, proto_decl_order=1),
                dump_field("object_", "Object", 40, FieldCategoryEnum.REPEATED, proto_decl_order=2),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="abc",
            fields=[
                dump_field("e3", "Fccc", 40, FieldCategoryEnum.REPEATED),
                dump_field("e1", "Faaa", 24, FieldCategoryEnum.STRING),
                dump_field("e2", "Faab", 32, FieldCategoryEnum.ENUM),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Chat.Message",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(REPEATED_MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, STRING_SHAPE),
                field_signature(32, ENUM_SHAPE),
                field_signature(40, REPEATED_MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset(
                {FieldKey(24, "content_"), FieldKey(32, "channel_"), FieldKey(40, "object_")}
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "abc",
            declared_field_signatures=[
                declared_field_signature(STRING_SHAPE),
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(REPEATED_MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, STRING_SHAPE),
                field_signature(32, ENUM_SHAPE),
                field_signature(40, REPEATED_MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "e1"), FieldKey(32, "e2"), FieldKey(40, "e3")}),
            dump_cs_msg=obf_message,
        )

        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            runtime_data_store=RuntimeDataStore(),
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        assert result[0].field_mapping == {
            "faaa": "content",
            "faab": "channel",
            "fccc": "object",
        }

    def test_maps_synthetic_oneof_variants_by_oneof_order_key_not_field_list_order(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_backing_field = dump_field("content_", None, 24, FieldCategoryEnum.ONEOF)
        non_obf_enum_field = dump_field("contentCase_", None, 32, FieldCategoryEnum.ENUM)
        non_obf_request = dump_field("Request", "Request", 24, FieldCategoryEnum.MESSAGE)
        non_obf_request.oneof_group_name = "content"
        non_obf_request.is_synthetic_oneof_variant = True
        non_obf_request.proto_decl_order = 0
        non_obf_response = dump_field("Response", "Response", 24, FieldCategoryEnum.MESSAGE)
        non_obf_response.oneof_group_name = "content"
        non_obf_response.is_synthetic_oneof_variant = True
        non_obf_response.proto_decl_order = 1
        non_obf_event = dump_field("Event", "Event", 24, FieldCategoryEnum.MESSAGE)
        non_obf_event.oneof_group_name = "content"
        non_obf_event.is_synthetic_oneof_variant = True
        non_obf_event.proto_decl_order = 2
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="Message",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol",
            fields=[
                non_obf_backing_field,
                non_obf_enum_field,
                non_obf_request,
                non_obf_response,
                non_obf_event,
            ],
        )

        obf_backing_field = dump_field("dttm", None, 32, FieldCategoryEnum.ONEOF)
        obf_enum_field = dump_field("dttn", None, 40, FieldCategoryEnum.ENUM)
        obf_event = dump_field("ezqp", "ezqp", 32, FieldCategoryEnum.MESSAGE)
        obf_event.oneof_group_name = "dttm"
        obf_event.is_synthetic_oneof_variant = True
        obf_event.proto_decl_order = 10_002
        obf_request = dump_field("ezqr", "ezqr", 32, FieldCategoryEnum.MESSAGE)
        obf_request.oneof_group_name = "dttm"
        obf_request.is_synthetic_oneof_variant = True
        obf_request.proto_decl_order = 10_000
        obf_response = dump_field("ezqq", "ezqq", 32, FieldCategoryEnum.MESSAGE)
        obf_response.oneof_group_name = "dttm"
        obf_response.is_synthetic_oneof_variant = True
        obf_response.proto_decl_order = 10_001
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="guc",
            fields=[
                obf_backing_field,
                obf_enum_field,
                obf_event,
                obf_request,
                obf_response,
            ],
        )

        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Message",
            declared_field_signatures=[
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(ENUM_SHAPE),
            ],
            field_signatures=[
                field_signature(24, MESSAGE_SHAPE),
                field_signature(32, ENUM_SHAPE),
            ],
            live_field_keys=frozenset(
                {
                    FieldKey(24, "Request"),
                    FieldKey(24, "Response"),
                    FieldKey(24, "Event"),
                    FieldKey(32, "contentCase_"),
                }
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "guc",
            declared_field_signatures=[
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
                declared_field_signature(ENUM_SHAPE),
            ],
            field_signatures=[
                field_signature(32, MESSAGE_SHAPE),
                field_signature(40, ENUM_SHAPE),
            ],
            live_field_keys=frozenset(
                {FieldKey(32, "ezqp"), FieldKey(32, "ezqr"), FieldKey(32, "ezqq"), FieldKey(40, "dttn")}
            ),
            dump_cs_msg=obf_message,
        )

        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
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

        assert result[0].field_mapping == {
            "ezqp": "request",
            "ezqr": "response",
            "ezqq": "event",
        }

    def test_score_pair_with_matching_access_and_declared_signatures_returns_perfect_score(
        self,
    ) -> None:
        declared_field_signature(NUMBER_SHAPE)
        non_obf_field = dump_field("value_", "Value", 24, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("e1", "Faaa", 24, FieldCategoryEnum.NUMBER)
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="ValueHolder")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="ObfValueHolder")

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(24, NUMBER_SHAPE),
            obf_access_signature=field_signature(24, NUMBER_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(RuntimeDataStore()),
            matching_store=None,
            pinned_pair=None,
        )

        assert score == 1.0
        assert metadata.child_match is None

    def test_score_pair_prefers_matching_enum_signature_over_other_enum_candidate(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        declared_field_signature(ENUM_SHAPE)
        non_obf_field = enum_field(
            field_name="channel_",
            property_name="Channel",
            offset=24,
            enum_type="ChatChannel",
        )
        good_obf_field = enum_field(
            field_name="ea",
            property_name="Ea",
            offset=32,
            enum_type="obf_chat_channel",
        )
        bad_obf_field = enum_field(
            field_name="eb",
            property_name="Eb",
            offset=24,
            enum_type="obf_chat_outcome",
        )
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="ChatRequest")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="jut")
        field_mapping_context = make_field_mapping_context(
            runtime_data_store,
            obf_enum_signatures_by_name={
                "obf_chat_channel": enum_entry([0], [1]),
                "obf_chat_outcome": EnumSignatureEntry(
                    member_value_to_name={"0": "Failure", "1": "Retry"},
                    switch_patterns=[],
                ),
            },
            non_obf_enum_signatures_by_name={
                "ChatChannel": enum_entry([0], [1]),
            },
        )

        good_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, ENUM_SHAPE),
            obf_access_signature=field_signature(32, ENUM_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=good_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )
        bad_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, ENUM_SHAPE),
            obf_access_signature=field_signature(24, ENUM_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=bad_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )

        assert good_score > bad_score

    def test_score_pair_uses_enum_key_signature_for_map_fields(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        declared_field_signature(FieldTypeShape(FieldCategoryEnum.MAP, FieldTypeLeafKind.ENUM, None))
        non_obf_field = map_enum_field(
            field_name="channel_by_id_",
            property_name="ChannelById",
            offset=24,
            enum_key_type="ChatChannel",
        )
        good_obf_field = map_enum_field(
            field_name="ea",
            property_name="Ea",
            offset=32,
            enum_key_type="obf_chat_channel",
        )
        bad_obf_field = map_enum_field(
            field_name="eb",
            property_name="Eb",
            offset=24,
            enum_key_type="obf_chat_outcome",
        )
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="ChatRequest")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="jut")
        field_mapping_context = make_field_mapping_context(
            runtime_data_store,
            obf_enum_signatures_by_name={
                "obf_chat_channel": enum_entry([0], [1]),
                "obf_chat_outcome": EnumSignatureEntry(
                    member_value_to_name={"0": "Failure", "1": "Retry"},
                    switch_patterns=[],
                ),
            },
            non_obf_enum_signatures_by_name={"ChatChannel": enum_entry([0], [1])},
        )
        map_enum_shape = FieldTypeShape(FieldCategoryEnum.MAP, FieldTypeLeafKind.ENUM, None)

        good_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, map_enum_shape),
            obf_access_signature=field_signature(32, map_enum_shape),
            non_obf_field=non_obf_field,
            obf_field=good_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )
        bad_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, map_enum_shape),
            obf_access_signature=field_signature(24, map_enum_shape),
            non_obf_field=non_obf_field,
            obf_field=bad_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )

        assert good_score > bad_score

    def test_score_pair_rejects_zero_enum_similarity_when_override_hint_exists(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        declared_field_signature(ENUM_SHAPE)
        non_obf_field = enum_field(
            field_name="channel_",
            property_name="Channel",
            offset=24,
            enum_type="ChatChannel",
        )
        obf_field = enum_field(
            field_name="ea",
            property_name="Ea",
            offset=24,
            enum_type="obf_chat_outcome",
        )
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ChatRequest",
            namespace="Com.Ankama.Chat",
        )
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="jut")
        score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, ENUM_SHAPE),
            obf_access_signature=field_signature(24, ENUM_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(
                runtime_data_store,
                signature_overrides_by_non_obf_cls={
                    non_obf_message.composed_name: SignatureOverrideEntry(
                        function_signatures=[],
                        field_signatures={},
                        enum_signature_hints_by_non_obf_prop_name={
                            "channel": {
                                "value": EnumSignatureOverrideHint(
                                    non_obf_enum_type="ChatChannel",
                                    signature=enum_entry(
                                        [10],
                                        [11],
                                        member_names={"10": "Global", "11": "Team"},
                                    ),
                                )
                            }
                        },
                    )
                },
                obf_enum_signatures_by_name={
                    "obf_chat_outcome": EnumSignatureEntry(
                        member_value_to_name={"0": "Failure", "1": "Retry"},
                        switch_patterns=[],
                    ),
                },
                non_obf_enum_signatures_by_name={
                    "ChatChannel": enum_entry([0], [1]),
                },
            ),
            matching_store=None,
            pinned_pair=None,
        )

        assert score == 0.0

    def test_build_field_mapping_uses_enum_hints_to_break_enum_field_ties(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="ChatRequest",
            namespace="Com.Ankama.Chat",
            fields=[
                enum_field(
                    field_name="channel_",
                    property_name="Channel",
                    offset=24,
                    enum_type="ChatChannel",
                ),
                enum_field(
                    field_name="outcome_",
                    property_name="Outcome",
                    offset=32,
                    enum_type="ChatOutcome",
                ),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="jut",
            fields=[
                enum_field(
                    field_name="ea",
                    property_name="Ea",
                    offset=24,
                    enum_type="obf_chat_outcome",
                ),
                enum_field(
                    field_name="eb",
                    property_name="Eb",
                    offset=32,
                    enum_type="obf_chat_channel",
                ),
            ],
        )
        non_obf_signature = message_signature(
            "Com.Ankama.Chat.ChatRequest",
            declared_field_signatures=[
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(ENUM_SHAPE),
            ],
            field_signatures=[
                field_signature(24, ENUM_SHAPE),
                field_signature(32, ENUM_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "channel_"), FieldKey(32, "outcome_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "jut",
            declared_field_signatures=[
                declared_field_signature(ENUM_SHAPE),
                declared_field_signature(ENUM_SHAPE),
            ],
            field_signatures=[
                field_signature(24, ENUM_SHAPE),
                field_signature(32, ENUM_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "ea"), FieldKey(32, "eb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_signature,
            obf_signature=obf_signature,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(
                runtime_data_store,
                signature_overrides_by_non_obf_cls={
                    non_obf_signature.message_cls: SignatureOverrideEntry(
                        function_signatures=[],
                        field_signatures={},
                        enum_signature_hints_by_non_obf_prop_name={
                            "channel": {
                                "value": EnumSignatureOverrideHint(
                                    non_obf_enum_type="ChatChannel",
                                    signature=enum_entry([100], [200]),
                                )
                            },
                            "outcome": {
                                "value": EnumSignatureOverrideHint(
                                    non_obf_enum_type="ChatOutcome",
                                    signature=EnumSignatureEntry(
                                        member_value_to_name={"300": "Success", "301": "Error"},
                                        switch_patterns=[],
                                    ),
                                )
                            },
                        },
                    )
                },
                obf_enum_signatures_by_name={
                    "obf_chat_channel": enum_entry([100], [200]),
                    "obf_chat_outcome": EnumSignatureEntry(
                        member_value_to_name={"300": "Success", "301": "Error"},
                        switch_patterns=[],
                    ),
                },
                non_obf_enum_signatures_by_name={
                    "ChatChannel": enum_entry([100], [200]),
                    "ChatOutcome": EnumSignatureEntry(
                        member_value_to_name={"300": "Success", "301": "Error"},
                        switch_patterns=[],
                    ),
                },
            ),
        )

        assert result.field_mapping == {
            "ea": "outcome",
            "eb": "channel",
        }

    def test_score_pair_averages_override_hint_scores_across_map_enum_slots(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        map_dual_enum_shape = FieldTypeShape(
            FieldCategoryEnum.MAP, FieldTypeLeafKind.ENUM, FieldTypeLeafKind.ENUM
        )
        declared_field_signature(map_dual_enum_shape)
        non_obf_field = map_enum_field(
            field_name="status_by_channel_",
            property_name="StatusByChannel",
            offset=24,
            enum_key_type="ChatChannel",
            enum_value_type="ChatOutcome",
        )
        good_obf_field = map_enum_field(
            field_name="ea",
            property_name="Ea",
            offset=24,
            enum_key_type="obf_chat_channel",
            enum_value_type="obf_chat_outcome",
        )
        partial_obf_field = map_enum_field(
            field_name="eb",
            property_name="Eb",
            offset=24,
            enum_key_type="obf_chat_channel",
            enum_value_type="obf_other_outcome",
        )
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection",
            name="ChatRequest",
            namespace="Com.Ankama.Chat",
        )
        obf_message = DumpCSMessage(file_descriptor="ChatReflection", name="jut")
        field_mapping_context = make_field_mapping_context(
            runtime_data_store,
            signature_overrides_by_non_obf_cls={
                non_obf_message.composed_name: SignatureOverrideEntry(
                    function_signatures=[],
                    field_signatures={},
                    enum_signature_hints_by_non_obf_prop_name={
                        "status_by_channel": {
                            "key": EnumSignatureOverrideHint(
                                non_obf_enum_type="ChatChannel",
                                signature=enum_entry([100], [200]),
                            ),
                            "value": EnumSignatureOverrideHint(
                                non_obf_enum_type="ChatOutcome",
                                signature=enum_entry([300], [301]),
                            ),
                        }
                    },
                )
            },
            obf_enum_signatures_by_name={
                "obf_chat_channel": enum_entry([100], [200]),
                "obf_chat_outcome": enum_entry([300], [301]),
                "obf_other_outcome": EnumSignatureEntry(
                    member_value_to_name={"0": "Failure", "1": "Retry"},
                    switch_patterns=[],
                ),
            },
        )

        good_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, map_dual_enum_shape),
            obf_access_signature=field_signature(24, map_dual_enum_shape),
            non_obf_field=non_obf_field,
            obf_field=good_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )
        partial_score, _ = score_field_pair(
            non_obf_access_signature=field_signature(24, map_dual_enum_shape),
            obf_access_signature=field_signature(24, map_dual_enum_shape),
            non_obf_field=non_obf_field,
            obf_field=partial_obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )

        assert good_score > partial_score

    def test_score_pair_vetoes_invalid_runtime_field_values(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        declared_field_signature(NUMBER_SHAPE)
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="MapCurrentEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="irj")
        non_obf_field = dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("fgvo", "Fgvo", 24, FieldCategoryEnum.NUMBER)
        seed_runtime_content(tmp_path, {"irj": [runtime_entry({"fgvo": 123})]})

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(24, NUMBER_SHAPE),
            obf_access_signature=field_signature(24, NUMBER_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            matching_store=None,
            pinned_pair=None,
        )

        assert score == 0.0
        assert metadata.child_match is None
        assert metadata.failed_validation_value == 123

    def test_pinned_field_pair_still_fails_when_runtime_validation_rejects_it(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        declared_field_signature(NUMBER_SHAPE)
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="MapCurrentEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="irj")
        non_obf_field = dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("fgvo", "Fgvo", 24, FieldCategoryEnum.NUMBER)
        seed_runtime_content(tmp_path, {"irj": [runtime_entry({"fgvo": 123})]})

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(24, NUMBER_SHAPE),
            obf_access_signature=field_signature(24, NUMBER_SHAPE),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            matching_store=None,
            pinned_pair=PinnedPair(
                obf="irj",
                non_obf="MapCurrentEvent",
                field_mapping_by_obf={"fgvo": "map_id"},
            ),
        )

        assert score == 0.0
        assert metadata.did_validation_failure is True

    def test_score_pair_accepts_array_like_runtime_values_for_cells(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        repeated_number_shape = FieldTypeShape(FieldCategoryEnum.REPEATED, FieldTypeLeafKind.NUMBER, None)
        declared_field_signature(repeated_number_shape)
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="MapMovementEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="irl")
        non_obf_field = dump_field("cells_", "Cells", 32, FieldCategoryEnum.REPEATED)
        obf_field = dump_field("efeh", "fhtm", 48, FieldCategoryEnum.REPEATED)
        non_obf_field.normalized_type = "RepeatedField<int>"
        non_obf_field.clr_type = "RepeatedField<int>"
        obf_field.normalized_type = "RepeatedField<int>"
        obf_field.clr_type = "RepeatedField<int>"
        seed_runtime_content(tmp_path, {"irl": [runtime_entry({"fhtm": np.array([480, 493])})]})

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(32, repeated_number_shape),
            obf_access_signature=field_signature(48, repeated_number_shape),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            matching_store=None,
            pinned_pair=None,
        )

        assert score > 0.9
        assert metadata.did_validation_failure is False

    def test_pinned_field_pair_keeps_runtime_bonus_when_validation_succeeds(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        repeated_number_shape = FieldTypeShape(FieldCategoryEnum.REPEATED, FieldTypeLeafKind.NUMBER, None)
        declared_field_signature(repeated_number_shape)
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="MapMovementEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="irl")
        non_obf_field = dump_field("cells_", "Cells", 32, FieldCategoryEnum.REPEATED)
        obf_field = dump_field("efeh", "fhtm", 48, FieldCategoryEnum.REPEATED)
        non_obf_field.normalized_type = "RepeatedField<int>"
        non_obf_field.clr_type = "RepeatedField<int>"
        obf_field.normalized_type = "RepeatedField<int>"
        obf_field.clr_type = "RepeatedField<int>"
        seed_runtime_content(tmp_path, {"irl": [runtime_entry({"fhtm": np.array([480, 493])})]})

        score, metadata = score_field_pair(
            non_obf_access_signature=field_signature(32, repeated_number_shape),
            obf_access_signature=field_signature(48, repeated_number_shape),
            non_obf_field=non_obf_field,
            obf_field=obf_field,
            non_obf_message=non_obf_message,
            obf_message=obf_message,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            non_obf_type_index={},
            obf_type_index={},
            non_obf_child_cls_by_field_key={},
            obf_child_cls_by_field_key={},
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            matching_store=None,
            pinned_pair=PinnedPair(
                obf="irl",
                non_obf="MapMovementEvent",
                field_mapping_by_obf={"fhtm": "cells"},
            ),
        )

        assert score > 1.0
        assert metadata.did_validation_failure is False

    def test_match_messages_maps_map_movement_cells_from_array_like_runtime_values(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        repeated_number_shape = FieldTypeShape(FieldCategoryEnum.REPEATED, FieldTypeLeafKind.NUMBER, None)
        boolean_shape = FieldTypeShape(FieldCategoryEnum.BOOLEAN, None, None)
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapMovementEvent",
            namespace="Com.Ankama.Dofus.Server.Game.Protocol.Gamemap",
            fields=[
                dump_field("cells_", "Cells", 32, FieldCategoryEnum.REPEATED, proto_decl_order=0),
                dump_field("character_id_", "CharacterId", 48, FieldCategoryEnum.NUMBER, proto_decl_order=1),
                dump_field("cautious_", "Cautious", 56, FieldCategoryEnum.BOOLEAN, proto_decl_order=2),
            ],
        )
        non_obf_message.fields[0].normalized_type = "RepeatedField<int>"
        non_obf_message.fields[0].clr_type = "RepeatedField<int>"
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="irl",
            fields=[
                dump_field("efeb", "fhtj", 32, FieldCategoryEnum.NUMBER),
                dump_field("efeh", "fhtm", 48, FieldCategoryEnum.REPEATED),
                dump_field("efej", "fhtn", 56, FieldCategoryEnum.BOOLEAN),
            ],
        )
        obf_message.fields[1].normalized_type = "RepeatedField<int>"
        obf_message.fields[1].clr_type = "RepeatedField<int>"

        non_obf_signature = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Gamemap.MapMovementEvent",
            declared_field_signatures=[
                declared_field_signature(repeated_number_shape),
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(boolean_shape),
            ],
            field_signatures=[
                field_signature(32, repeated_number_shape),
                field_signature(48, NUMBER_SHAPE),
                field_signature(56, boolean_shape),
            ],
            live_field_keys=frozenset(
                {FieldKey(32, "cells_"), FieldKey(48, "character_id_"), FieldKey(56, "cautious_")}
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_signature = message_signature(
            "irl",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(repeated_number_shape),
                declared_field_signature(boolean_shape),
            ],
            field_signatures=[
                field_signature(32, NUMBER_SHAPE),
                field_signature(48, repeated_number_shape),
                field_signature(56, boolean_shape),
            ],
            live_field_keys=frozenset({FieldKey(32, "efeb"), FieldKey(48, "efeh"), FieldKey(56, "efej")}),
            dump_cs_msg=obf_message,
        )

        seed_runtime_content(
            tmp_path,
            {"irl": [runtime_entry({"fhtm": np.array([480, 493])}, from_server=True)]},
        )
        result = match_messages_for_test(
            [obf_signature],
            [non_obf_signature],
            obf_messages_by_cls=build_message_lookup([obf_message]),
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

        assert result[0].field_mapping == {
            "fhtj": "character_id",
            "fhtm": "cells",
            "fhtn": "cautious",
        }
