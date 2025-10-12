from pathlib import Path

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.enum_builders import enum_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import (
    dump_field,
    enum_field,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    build_message_lookup,
    field_signature,
    make_field_mapping_context,
)
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_builders import runtime_entry
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.runtime_store import seed_runtime_content
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.shapes import (
    ENUM_SHAPE,
    NUMBER_SHAPE,
    REPEATED_MESSAGE_SHAPE,
)

from DBDofusUnity.proto_mapper_assembly.field_mapping.field_mapping_scoring import score_field_pair
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage
from DBDofusUnity.proto_mapper_assembly.interfaces.enum_mapping import EnumSignatureEntry
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.signature_overrides import (
    EnumSignatureOverrideHint,
    SignatureOverrideEntry,
)
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


class TestZeroScoreReasons:
    """Tests that score_field_pair sets zero_score_reason on metadata for each early-exit case."""

    def test_zero_score_reason_validation_failure(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="MapCurrentEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="irj")
        non_obf_field = dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("fgvo", "Fgvo", 24, FieldCategoryEnum.NUMBER)
        seed_runtime_content(tmp_path, {"irj": [runtime_entry({"fgvo": 123})]})

        _, metadata = score_field_pair(
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

        assert metadata.zero_score_reason == "validation_failure"
        assert metadata.failed_validation_value == 123

    def test_zero_score_reason_child_score_too_low(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_child = DumpCSMessage(file_descriptor="GameReflection", name="StatedElement")
        obf_child = DumpCSMessage(file_descriptor="GameReflection", name="kgp")
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapComplementaryInformationEvent",
            fields=[dump_field("stated_elements_", "StatedElements", 24, FieldCategoryEnum.REPEATED)],
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

        _, metadata = score_field_pair(
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
                score_by_pair={MatchPairKey("kgp", "StatedElement"): 0.05},
            ),
            matching_store=None,
            pinned_pair=None,
        )

        assert metadata.zero_score_reason == "child_score_too_low"

    def test_zero_score_reason_enum_override_conflict(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="ChatReflection", name="ChatRequest", namespace="Com.Ankama.Chat"
        )
        obf_message = DumpCSMessage(file_descriptor="ChatReflection", name="jut")
        obf_field = enum_field(field_name="ea", property_name="Ea", offset=24, enum_type="obf_chat_outcome")
        non_obf_field = enum_field(
            field_name="channel_", property_name="Channel", offset=24, enum_type="ChatChannel"
        )
        field_mapping_context = make_field_mapping_context(
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
        )

        score, metadata = score_field_pair(
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
            field_mapping_context=field_mapping_context,
            matching_store=None,
            pinned_pair=None,
        )

        assert score == 0.0
        assert metadata.zero_score_reason == "enum_override_conflict"

    def test_no_zero_score_reason_when_pair_is_valid(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="SomeEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="isu")
        non_obf_field = dump_field("item_id_", "ItemId", 24, FieldCategoryEnum.NUMBER)
        obf_field = dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.NUMBER)

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

        assert score > 0.0
        assert metadata.zero_score_reason is None
