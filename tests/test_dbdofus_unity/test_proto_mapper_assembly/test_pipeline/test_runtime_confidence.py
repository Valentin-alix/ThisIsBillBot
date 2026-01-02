from pathlib import Path
from unittest.mock import patch

from tests.fixtures.proto_mapper.field_builders import typed_dump_field
from tests.fixtures.proto_mapper.message_builders import (
    EMPTY_ACCESS_TRACE,
    build_message_lookup,
    build_verified_mapping,
    field_signature,
    message_signature,
)
from tests.fixtures.proto_mapper.runtime_builders import runtime_entry
from tests.fixtures.proto_mapper.runtime_store import seed_runtime_content
from tests.fixtures.proto_mapper.shapes import (
    MESSAGE_SHAPE,
    NUMBER_SHAPE,
    REPEATED_MESSAGE_SHAPE,
)
from tests.fixtures.proto_mapper.signatures import declared_field_signature

from tests.fixtures.proto_mapper.matching_builders import (
    match_messages_for_test,
)

from DBDofusUnity.proto_mapper_assembly.interfaces.capture_sequence_hints import CaptureSequenceHintsConfig
from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_field_validation import build_runtime_field_validator_confidence
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore
from DBDofusUnity.proto_mapper_assembly.validators.field_validators import ValidatorFn


class TestRuntimeConfidence:
    def test_live_field_scoring_ignores_dead_fields(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_event = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapCurrentEvent",
            fields=[
                typed_dump_field(
                    field_name="map_id_",
                    property_name="MapId",
                    normalized_type="long",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        non_obf_instance = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapCurrentInstanceEvent",
            fields=[
                typed_dump_field(
                    field_name="map_id_",
                    property_name="MapId",
                    normalized_type="long",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="instantiate_map_id_",
                    property_name="InstantiateMapId",
                    normalized_type="long",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )
        obf_irj = DumpCSMessage(
            file_descriptor="GameReflection",
            name="irj",
            fields=[
                typed_dump_field(
                    field_name="eenp",
                    property_name="Fgvo",
                    normalized_type="long",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="eenr",
                    property_name="Fgvp",
                    normalized_type="long",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )

        matches = match_messages_for_test(
            [
                message_signature(
                    "irj",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "eenp")}),
                    dump_cs_msg=obf_irj,
                )
            ],
            [
                message_signature(
                    "MapCurrentEvent",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "map_id_")}),
                    dump_cs_msg=non_obf_event,
                ),
                message_signature(
                    "MapCurrentInstanceEvent",
                    declared_field_signatures=[
                        declared_field_signature(NUMBER_SHAPE),
                        declared_field_signature(NUMBER_SHAPE),
                    ],
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                    ],
                    live_field_keys=frozenset(
                        {FieldKey(0x18, "map_id_"), FieldKey(0x20, "instantiate_map_id_")}
                    ),
                    dump_cs_msg=non_obf_instance,
                ),
            ],
            obf_messages_by_cls=build_message_lookup([obf_irj]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_event, non_obf_instance]),
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
        assert matches[0].non_obf_signature.message_cls == "MapCurrentEvent"

    def test_pipeline_keeps_root_runtime_confidence_none_for_nested_samples(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="InventoryEvent",
            fields=[
                typed_dump_field(
                    field_name="object_",
                    property_name="Object",
                    normalized_type="ObjectItem",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="obf_root",
            fields=[
                typed_dump_field(
                    field_name="obf_object",
                    property_name="obj",
                    normalized_type="obf_item",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        non_obf_child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ObjectItem",
            fields=[
                typed_dump_field(
                    field_name="uid_",
                    property_name="Uid",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="quantity_",
                    property_name="Quantity",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )
        obf_child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="obf_item",
            fields=[
                typed_dump_field(
                    field_name="uid_obf",
                    property_name="u1",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="quantity_obf",
                    property_name="q1",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )
        seed_runtime_content(
            tmp_path,
            {
                "obf_root": [
                    runtime_entry({"obj": {"u1": 10, "q1": 1}}, from_server=True),
                    runtime_entry({"obj": {"u1": 11, "q1": 2}}, from_server=True),
                    runtime_entry({"obj": {"u1": 12, "q1": 3}}, from_server=True),
                    runtime_entry({"obj": {"u1": 13, "q1": 4}}, from_server=True),
                    runtime_entry({"obj": {"u1": 14, "q1": 5}}, from_server=True),
                ]
            },
        )

        matches = match_messages_for_test(
            [
                message_signature(
                    "obf_root",
                    declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                    field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "obf_object")}),
                    dump_cs_msg=obf_root,
                ),
                message_signature(
                    "obf_item",
                    declared_field_signatures=[
                        declared_field_signature(NUMBER_SHAPE),
                        declared_field_signature(NUMBER_SHAPE),
                    ],
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                    ],
                    live_field_keys=frozenset({FieldKey(0x18, "uid_obf"), FieldKey(0x20, "quantity_obf")}),
                    dump_cs_msg=obf_child,
                ),
            ],
            [
                message_signature(
                    "InventoryEvent",
                    declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                    field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "object_")}),
                    dump_cs_msg=non_obf_root,
                ),
                message_signature(
                    "ObjectItem",
                    declared_field_signatures=[
                        declared_field_signature(NUMBER_SHAPE),
                        declared_field_signature(NUMBER_SHAPE),
                    ],
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                    ],
                    live_field_keys=frozenset({FieldKey(0x18, "uid_"), FieldKey(0x20, "quantity_")}),
                    dump_cs_msg=non_obf_child,
                ),
            ],
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        matches_by_non_obf = {match.non_obf_signature.message_cls: match for match in matches}
        assert matches_by_non_obf["InventoryEvent"].runtime_confidence is None

    def test_pipeline_parent_constrained_child_mapping_has_no_root_runtime_confidence(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="InventoryEvent",
            fields=[
                typed_dump_field(
                    field_name="object_",
                    property_name="Object",
                    normalized_type="ObjectItem",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        non_obf_child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ObjectItem",
            fields=[
                typed_dump_field(
                    field_name="uid_",
                    property_name="Uid",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="quantity_",
                    property_name="Quantity",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )
        wrong_non_obf_child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SpellModifier",
            fields=[
                typed_dump_field(
                    field_name="spell_id_",
                    property_name="SpellId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="obf_root",
            fields=[
                typed_dump_field(
                    field_name="obf_object",
                    property_name="obj",
                    normalized_type="obf_item",
                    category=FieldCategoryEnum.MESSAGE,
                    offset=0x18,
                )
            ],
        )
        obf_child = DumpCSMessage(
            file_descriptor="GameReflection",
            name="obf_item",
            fields=[
                typed_dump_field(
                    field_name="uid_obf",
                    property_name="u1",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        seed_runtime_content(
            tmp_path,
            {
                "obf_root": [runtime_entry({"obj": {"u1": 10}}, from_server=True)],
                "obf_item": [runtime_entry({"u1": 10}, is_root_msg=False)],
            },
        )

        matches = match_messages_for_test(
            [
                message_signature(
                    "obf_root",
                    declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                    field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "obf_object")}),
                    dump_cs_msg=obf_root,
                ),
                message_signature(
                    "obf_item",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "uid_obf")}),
                    dump_cs_msg=obf_child,
                ),
            ],
            [
                message_signature(
                    "InventoryEvent",
                    declared_field_signatures=[declared_field_signature(MESSAGE_SHAPE)],
                    field_signatures=[field_signature(0x18, MESSAGE_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "object_")}),
                    dump_cs_msg=non_obf_root,
                ),
                message_signature(
                    "SpellModifier",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    live_field_keys=frozenset({FieldKey(0x18, "spell_id_")}),
                    dump_cs_msg=wrong_non_obf_child,
                ),
                message_signature(
                    "ObjectItem",
                    declared_field_signatures=[
                        declared_field_signature(NUMBER_SHAPE),
                        declared_field_signature(NUMBER_SHAPE),
                    ],
                    field_signatures=[
                        field_signature(0x18, NUMBER_SHAPE),
                        field_signature(0x20, NUMBER_SHAPE),
                    ],
                    live_field_keys=frozenset({FieldKey(0x18, "uid_"), FieldKey(0x20, "quantity_")}),
                    dump_cs_msg=non_obf_child,
                ),
            ],
            obf_messages_by_cls=build_message_lookup([obf_root, obf_child]),
            non_obf_messages_by_cls=build_message_lookup([non_obf_root, non_obf_child, wrong_non_obf_child]),
            runtime_data_store=runtime_data_store,
            pinned_pairs_config=build_verified_mapping(),
            capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
            signature_overrides_by_non_obf_cls={},
            obf_enum_signatures_by_name={},
            non_obf_enum_signatures_by_name={},
            obf_access_trace=EMPTY_ACCESS_TRACE,
            non_obf_access_trace=EMPTY_ACCESS_TRACE,
        )

        matches_by_non_obf = {match.non_obf_signature.message_cls: match for match in matches}
        assert matches_by_non_obf["InventoryEvent"].runtime_confidence is None

    def test_pipeline_keeps_runtime_confidence_none_without_samples(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="obf_simple")
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="SimpleMessage")

        matches = match_messages_for_test(
            [
                message_signature(
                    "obf_simple",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    dump_cs_msg=obf_message,
                )
            ],
            [
                message_signature(
                    "SimpleMessage",
                    declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                    field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                    dump_cs_msg=non_obf_message,
                )
            ],
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

        assert matches[0].runtime_confidence is None

    def test_pipeline_uses_runtime_refined_child_scores_for_root_field_mapping(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapComplementaryInformationEvent",
            fields=[
                typed_dump_field(
                    field_name="interactive_elements_",
                    property_name="InteractiveElements",
                    normalized_type="RepeatedField<InteractiveElement>",
                    category=FieldCategoryEnum.REPEATED,
                    offset=0x20,
                ),
                typed_dump_field(
                    field_name="stated_elements_",
                    property_name="StatedElements",
                    normalized_type="RepeatedField<StatedElement>",
                    category=FieldCategoryEnum.REPEATED,
                    offset=0x18,
                ),
            ],
        )
        obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[
                typed_dump_field(
                    field_name="fhdb",
                    property_name="Fhdb",
                    normalized_type="RepeatedField<kmv>",
                    category=FieldCategoryEnum.REPEATED,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="fhcu",
                    property_name="Fhcu",
                    normalized_type="RepeatedField<kgp>",
                    category=FieldCategoryEnum.REPEATED,
                    offset=0x20,
                ),
            ],
        )
        non_obf_interactive = DumpCSMessage(
            file_descriptor="GameReflection",
            name="InteractiveElement",
            fields=[
                typed_dump_field(
                    field_name="element_type_id_",
                    property_name="ElementTypeId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x14,
                ),
                typed_dump_field(
                    field_name="element_id_",
                    property_name="ElementId",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
            ],
        )
        non_obf_stated = DumpCSMessage(
            file_descriptor="GameReflection",
            name="StatedElement",
            fields=[
                typed_dump_field(
                    field_name="state_",
                    property_name="State",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_interactive = DumpCSMessage(
            file_descriptor="GameReflection",
            name="kmv",
            fields=[
                typed_dump_field(
                    field_name="element_type_obf",
                    property_name="Foml",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x14,
                ),
                typed_dump_field(
                    field_name="value_obf",
                    property_name="Fomk",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
            ],
        )
        obf_stated = DumpCSMessage(
            file_descriptor="GameReflection",
            name="kgp",
            fields=[
                typed_dump_field(
                    field_name="value_obf",
                    property_name="Fnjt",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        seed_runtime_content(
            tmp_path,
            {
                "kmv": [runtime_entry({"foml": 3, "fomk": 42}, is_root_msg=False)],
                "kgp": [runtime_entry({"fnjt": -1}, is_root_msg=False)],
            },
        )

        validators_patch: dict[str, dict[str, ValidatorFn[int]]] = {
            "InteractiveElement": {"element_id": lambda value: value > 0},
            "StatedElement": {"state": lambda value: value < 0},
        }

        with patch.dict(
            "DBDofusUnity.proto_mapper_assembly.validators.field_validators.VALIDATORS_BY_NON_OBF_MESSAGE_NAME",
            validators_patch,
            clear=False,
        ):
            matches = match_messages_for_test(
                [
                    message_signature(
                        "isu",
                        declared_field_signatures=[
                            declared_field_signature(REPEATED_MESSAGE_SHAPE),
                            declared_field_signature(REPEATED_MESSAGE_SHAPE),
                        ],
                        field_signatures=[
                            field_signature(0x18, REPEATED_MESSAGE_SHAPE),
                            field_signature(0x20, REPEATED_MESSAGE_SHAPE),
                        ],
                        live_field_keys=frozenset({FieldKey(0x18, "fhdb"), FieldKey(0x20, "fhcu")}),
                        dump_cs_msg=obf_root,
                    ),
                    message_signature(
                        "kmv",
                        declared_field_signatures=[
                            declared_field_signature(NUMBER_SHAPE),
                            declared_field_signature(NUMBER_SHAPE),
                        ],
                        field_signatures=[
                            field_signature(0x14, NUMBER_SHAPE),
                            field_signature(0x18, NUMBER_SHAPE),
                        ],
                        live_field_keys=frozenset(
                            {FieldKey(0x14, "element_type_obf"), FieldKey(0x18, "value_obf")}
                        ),
                        dump_cs_msg=obf_interactive,
                    ),
                    message_signature(
                        "kgp",
                        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                        field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                        live_field_keys=frozenset({FieldKey(0x18, "value_obf")}),
                        dump_cs_msg=obf_stated,
                    ),
                ],
                [
                    message_signature(
                        "MapComplementaryInformationEvent",
                        declared_field_signatures=[
                            declared_field_signature(REPEATED_MESSAGE_SHAPE),
                            declared_field_signature(REPEATED_MESSAGE_SHAPE),
                        ],
                        field_signatures=[
                            field_signature(0x20, REPEATED_MESSAGE_SHAPE),
                            field_signature(0x18, REPEATED_MESSAGE_SHAPE),
                        ],
                        live_field_keys=frozenset(
                            {FieldKey(0x18, "stated_elements_"), FieldKey(0x20, "interactive_elements_")}
                        ),
                        dump_cs_msg=non_obf_root,
                    ),
                    message_signature(
                        "InteractiveElement",
                        declared_field_signatures=[
                            declared_field_signature(NUMBER_SHAPE),
                            declared_field_signature(NUMBER_SHAPE),
                        ],
                        field_signatures=[
                            field_signature(0x14, NUMBER_SHAPE),
                            field_signature(0x18, NUMBER_SHAPE),
                        ],
                        live_field_keys=frozenset(
                            {FieldKey(0x14, "element_type_id_"), FieldKey(0x18, "element_id_")}
                        ),
                        dump_cs_msg=non_obf_interactive,
                    ),
                    message_signature(
                        "StatedElement",
                        declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
                        field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
                        live_field_keys=frozenset({FieldKey(0x18, "state_")}),
                        dump_cs_msg=non_obf_stated,
                    ),
                ],
                obf_messages_by_cls=build_message_lookup([obf_root, obf_interactive, obf_stated]),
                non_obf_messages_by_cls=build_message_lookup(
                    [non_obf_root, non_obf_interactive, non_obf_stated]
                ),
                runtime_data_store=runtime_data_store,
                pinned_pairs_config=build_verified_mapping(),
                capture_sequence_hints_config=CaptureSequenceHintsConfig(sequences=()),
                signature_overrides_by_non_obf_cls={},
                obf_enum_signatures_by_name={},
                non_obf_enum_signatures_by_name={},
                obf_access_trace=EMPTY_ACCESS_TRACE,
                non_obf_access_trace=EMPTY_ACCESS_TRACE,
            )

        matches_by_non_obf = {match.non_obf_signature.message_cls: match for match in matches}
        assert matches_by_non_obf["InteractiveElement"].runtime_confidence == 1.0
        assert matches_by_non_obf["StatedElement"].runtime_confidence == 1.0
        assert matches_by_non_obf["MapComplementaryInformationEvent"].field_mapping == {
            "fhdb": "interactive_elements",
            "fhcu": "stated_elements",
        }

    def test_pipeline_uses_filtered_runtime_alias_for_nested_obf_message(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="NestedLeaf",
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
        non_obf_signature = message_signature(
            "NestedLeaf",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(0x18, "value_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_root = DumpCSMessage(
            file_descriptor="GameReflection",
            name="obf",
            fields=[
                typed_dump_field(
                    field_name="keep_root_",
                    property_name="KeepRoot",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x10,
                )
            ],
        )
        obf_container = DumpCSMessage(
            file_descriptor="GameReflection",
            name="container",
            parent_name="obf",
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="leaf",
            parent_name="obf.container",
            fields=[
                typed_dump_field(
                    field_name="fhcu",
                    property_name="Fhcu",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                )
            ],
        )
        obf_signature = message_signature(
            "obf.container.leaf",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(0x18, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(0x18, "fhcu")}),
            dump_cs_msg=obf_message,
        )
        obf_messages_by_cls = build_message_lookup([obf_root, obf_container, obf_message])
        seed_runtime_content(tmp_path, {"obf.leaf": [runtime_entry({"fhcu": 5})]})

        validators_patch: dict[str, dict[str, ValidatorFn[int]]] = {
            "NestedLeaf": {"value": lambda value: value > 0}
        }

        with patch.dict(
            "DBDofusUnity.proto_mapper_assembly.validators.field_validators.VALIDATORS_BY_NON_OBF_MESSAGE_NAME",
            validators_patch,
            clear=False,
        ):
            confidence = build_runtime_field_validator_confidence(
                field_mapping={"fhcu": "value"},
                obf_message=obf_signature.dump_cs_msg,
                obf_messages_by_cls=obf_messages_by_cls,
                non_obf_message=non_obf_signature.dump_cs_msg,
                validated_non_obf_field_names={"value"},
                runtime_data_store=runtime_data_store,
            )

        assert confidence == 1.0

    def test_confidence_ignores_validators_for_non_exportable_non_obf_fields(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ExchangeBidPriceEvent",
            fields=[
                typed_dump_field(
                    field_name="object_gid_",
                    property_name="ObjectGid",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x18,
                ),
                typed_dump_field(
                    field_name="average_price_",
                    property_name="AveragePrice",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                ),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="jip",
            fields=[
                typed_dump_field(
                    field_name="fltm",
                    property_name="Fltm",
                    normalized_type="int",
                    category=FieldCategoryEnum.NUMBER,
                    offset=0x20,
                )
            ],
        )
        seed_runtime_content(tmp_path, {"jip": [runtime_entry({"fltm": 100}, from_server=True)]})
        validators_patch: dict[str, dict[str, ValidatorFn[int]]] = {
            "ExchangeBidPriceEvent": {
                "object_gid": lambda runtime_value: runtime_value > 0,
                "average_price": lambda runtime_value: runtime_value > 0,
            }
        }

        with patch.dict(
            "DBDofusUnity.proto_mapper_assembly.validators.field_validators.VALIDATORS_BY_NON_OBF_MESSAGE_NAME",
            validators_patch,
            clear=False,
        ):
            confidence = build_runtime_field_validator_confidence(
                field_mapping={"fltm": "average_price"},
                obf_message=obf_message,
                obf_messages_by_cls=build_message_lookup([obf_message]),
                non_obf_message=non_obf_message,
                validated_non_obf_field_names={"average_price"},
                runtime_data_store=runtime_data_store,
            )

        assert confidence == 1.0

    def test_confidence_still_fails_when_exportable_validator_field_is_unmapped(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        non_obf_message = DumpCSMessage(file_descriptor="GameReflection", name="InteractiveUseErrorEvent")
        obf_message = DumpCSMessage(file_descriptor="GameReflection", name="iex")
        seed_runtime_content(tmp_path, {"iex": [runtime_entry({"fgzk": 10}, from_server=True)]})
        validators_patch: dict[str, dict[str, ValidatorFn[int]]] = {
            "InteractiveUseErrorEvent": {"skill_instance_uid": lambda runtime_value: runtime_value > 0}
        }

        with patch.dict(
            "DBDofusUnity.proto_mapper_assembly.validators.field_validators.VALIDATORS_BY_NON_OBF_MESSAGE_NAME",
            validators_patch,
            clear=False,
        ):
            confidence = build_runtime_field_validator_confidence(
                field_mapping={},
                obf_message=obf_message,
                obf_messages_by_cls=build_message_lookup([obf_message]),
                non_obf_message=non_obf_message,
                validated_non_obf_field_names={"skill_instance_uid"},
                runtime_data_store=runtime_data_store,
            )

        assert confidence == 0.0
