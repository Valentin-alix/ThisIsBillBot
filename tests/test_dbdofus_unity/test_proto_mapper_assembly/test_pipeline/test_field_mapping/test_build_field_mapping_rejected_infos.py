from pathlib import Path

from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.field_builders import dump_field
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.message_builders import (
    build_field_mapping_for_test,
    build_message_lookup,
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
from tests.test_dbdofus_unity.test_proto_mapper_assembly.fixture.signatures import (
    access_atom,
    declared_field_signature,
)
from pydantic import BaseModel

from DBDofusUnity.proto_mapper_assembly.interfaces.dump_cs_message import DumpCSMessage, FieldKey
from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.interfaces.field_mapping_rejected_infos import (
    FieldMappingRejectedInfos,
    ScoreRejectedInfo,
)
from DBDofusUnity.proto_mapper_assembly.interfaces.message_pair import MatchPairKey
from DBDofusUnity.proto_mapper_assembly.interfaces.pinned_pairs import PinnedPair
from DBDofusUnity.proto_mapper_assembly.runtime.runtime_store import RuntimeDataStore


def _dump_rejected_infos(infos: FieldMappingRejectedInfos) -> dict[str, dict[str, object]]:
    return {
        obf_field: {
            non_obf_field: rejected_info.model_dump()
            if isinstance(rejected_info, BaseModel)
            else rejected_info
            for non_obf_field, rejected_info in rejected_by_non_obf.items()
        }
        for obf_field, rejected_by_non_obf in infos.items()
    }


class TestBuildFieldMappingRejectedInfos:
    """Tests that build_field_mapping populates field_mapping_rejected_infos correctly."""

    def test_populates_rejected_infos_for_child_score_too_low(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
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
        non_obf_sig = message_signature(
            "MapComplementaryInformationEvent",
            declared_field_signatures=[],
            field_signatures=[field_signature(24, REPEATED_MESSAGE_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "stated_elements_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[],
            field_signatures=[field_signature(24, REPEATED_MESSAGE_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "fhdb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message, non_obf_child]),
            obf_messages_by_cls=build_message_lookup([obf_message, obf_child]),
            field_mapping_context=make_field_mapping_context(
                runtime_data_store,
                score_by_pair={MatchPairKey("kgp", "StatedElement"): 0.05},
            ),
            non_obf_type_index={"StatedElement": (non_obf_child,)},
            obf_type_index={"kgp": (obf_child,)},
        )

        assert result.field_mapping == {}
        assert _dump_rejected_infos(result.field_mapping_rejected_infos) == {
            "fhdb": {"stated_elements": {"reason": "not_selected", "score": 0.0}}
        }

    def test_populates_rejected_infos_for_validation_failure_value(
        self, runtime_data_store: RuntimeDataStore, tmp_path: Path
    ) -> None:
        seed_runtime_content(tmp_path, {"irj": [runtime_entry({"fgvo": 123})]})
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="MapCurrentEvent",
            fields=[dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER)],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="irj",
            fields=[dump_field("fgvo", "Fgvo", 24, FieldCategoryEnum.NUMBER)],
        )
        non_obf_sig = message_signature(
            "MapCurrentEvent",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "map_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "irj",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "fgvo")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {}
        assert _dump_rejected_infos(result.field_mapping_rejected_infos) == {
            "fgvo": {"map_id": {"reason": "validation_failure", "value": 123}}
        }

    def test_empty_rejected_infos_when_all_pairs_pass(self, runtime_data_store: RuntimeDataStore) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SomeEvent",
            fields=[dump_field("actor_id_", "ActorId", 24, FieldCategoryEnum.NUMBER)],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.NUMBER)],
        )
        non_obf_sig = message_signature(
            "SomeEvent",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "actor_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "fhdb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping_rejected_infos == {}
        assert result.field_mapping_unmapped_non_obf_fields == {}

    def test_populates_rejected_infos_for_valid_pairs_not_selected_by_assignment(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SomeEvent",
            fields=[
                dump_field("first_id_", "FirstId", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field("second_id_", "SecondId", 32, FieldCategoryEnum.NUMBER, proto_decl_order=1),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[
                dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field("fhdc", "Fhdc", 32, FieldCategoryEnum.NUMBER, proto_decl_order=1),
            ],
        )
        non_obf_sig = message_signature(
            "SomeEvent",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
            ],
            field_signatures=[
                field_signature(
                    24,
                    NUMBER_SHAPE,
                    accesses=[access_atom(field_type_shape=NUMBER_SHAPE, field_access_index=1)],
                ),
                field_signature(
                    32,
                    NUMBER_SHAPE,
                    accesses=[access_atom(field_type_shape=NUMBER_SHAPE, field_access_index=2)],
                ),
            ],
            live_field_keys=frozenset({FieldKey(24, "first_id_"), FieldKey(32, "second_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
            ],
            field_signatures=[
                field_signature(
                    24,
                    NUMBER_SHAPE,
                    accesses=[access_atom(field_type_shape=NUMBER_SHAPE, field_access_index=1)],
                ),
                field_signature(
                    32,
                    NUMBER_SHAPE,
                    accesses=[access_atom(field_type_shape=NUMBER_SHAPE, field_access_index=2)],
                ),
            ],
            live_field_keys=frozenset({FieldKey(24, "fhdb"), FieldKey(32, "fhdc")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {"fhdb": "first_id", "fhdc": "second_id"}
        # On vérifie la raison du rejet et la borne du score, pas la valeur exacte.
        # Le score précis dépend de la pondération des features de similarity, qui peut
        # évoluer (cf. plan : poids des compteurs fragiles abaissés) — on ne lock pas
        # cette valeur ici sinon le test casse à chaque rééquilibrage.
        for rejected_pair_key in (("fhdc", "first_id"), ("fhdb", "second_id")):
            obf_field, non_obf_field = rejected_pair_key
            rejected_info = result.field_mapping_rejected_infos[obf_field][non_obf_field]
            assert isinstance(rejected_info, ScoreRejectedInfo)
            assert rejected_info.reason == "not_selected"
            assert 0.0 < rejected_info.score <= 1.0

    def test_unmapped_non_obf_fields_no_obf_candidate_when_obf_has_fewer_fields(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SomeEvent",
            fields=[
                dump_field("map_id_", "MapId", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field("actor_id_", "ActorId", 32, FieldCategoryEnum.NUMBER, proto_decl_order=1),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.NUMBER)],
        )
        non_obf_sig = message_signature(
            "SomeEvent",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
            ],
            field_signatures=[
                field_signature(24, NUMBER_SHAPE),
                field_signature(32, NUMBER_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "map_id_"), FieldKey(32, "actor_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "fhdb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping_unmapped_non_obf_fields == {"actor_id": "no_obf_candidate"}

    def test_unmapped_non_obf_fields_score_below_threshold_when_types_incompatible(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SomeEvent",
            fields=[dump_field("content_", "Content", 24, FieldCategoryEnum.STRING, proto_decl_order=0)],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 32, FieldCategoryEnum.ENUM)],
        )
        non_obf_sig = message_signature(
            "SomeEvent",
            declared_field_signatures=[declared_field_signature(STRING_SHAPE)],
            field_signatures=[field_signature(24, STRING_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "content_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[declared_field_signature(ENUM_SHAPE)],
            field_signatures=[field_signature(32, ENUM_SHAPE)],
            live_field_keys=frozenset({FieldKey(32, "fhdb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {}
        assert result.field_mapping_unmapped_non_obf_fields == {"content": "score_below_threshold"}

    def test_unmapped_non_obf_field_without_live_access_is_reported(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="SomeEvent",
            fields=[
                dump_field("actor_id_", "ActorId", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field("object_gid_", "ObjectGid", 32, FieldCategoryEnum.NUMBER, proto_decl_order=1),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="isu",
            fields=[dump_field("fhdb", "Fhdb", 24, FieldCategoryEnum.NUMBER)],
        )
        non_obf_sig = message_signature(
            "SomeEvent",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "actor_id_")}),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "isu",
            declared_field_signatures=[declared_field_signature(NUMBER_SHAPE)],
            field_signatures=[field_signature(24, NUMBER_SHAPE)],
            live_field_keys=frozenset({FieldKey(24, "fhdb")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {"fhdb": "actor_id"}
        assert result.field_mapping_unmapped_non_obf_fields == {"object_gid": "no_obf_candidate"}

    def test_obf_field_without_live_access_is_still_mapped(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ExchangeBidPriceEvent",
            fields=[
                dump_field("object_gid_", "ObjectGid", 24, FieldCategoryEnum.NUMBER, proto_decl_order=0),
                dump_field(
                    "average_price_", "AveragePrice", 32, FieldCategoryEnum.NUMBER, proto_decl_order=1
                ),
                dump_field(
                    "bid_price_for_seller_",
                    "BidPriceForSeller",
                    40,
                    FieldCategoryEnum.MESSAGE,
                    proto_decl_order=2,
                ),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="jei",
            fields=[
                dump_field("fked", "fked", 24, FieldCategoryEnum.NUMBER),
                dump_field("fkee", "fkee", 32, FieldCategoryEnum.MESSAGE),
                dump_field("fkef", "fkef", 40, FieldCategoryEnum.NUMBER),
            ],
        )
        non_obf_sig = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Exchange.ExchangeBidPriceEvent",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, NUMBER_SHAPE),
                field_signature(32, NUMBER_SHAPE),
                field_signature(40, MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset(
                {
                    FieldKey(24, "object_gid_"),
                    FieldKey(32, "average_price_"),
                    FieldKey(40, "bid_price_for_seller_"),
                }
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "jei",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(24, NUMBER_SHAPE),
                field_signature(32, MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(24, "fked"), FieldKey(32, "fkee")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
        )

        assert result.field_mapping == {
            "fked": "object_gid",
            "fkee": "bid_price_for_seller",
            "fkef": "average_price",
        }
        assert _dump_rejected_infos(result.field_mapping_rejected_infos) == {
            "fked": {
                "average_price": {"reason": "not_selected", "score": 1.0},
                "bid_price_for_seller": {"reason": "not_selected", "score": 0.0},
            },
            "fkee": {
                "average_price": {"reason": "not_selected", "score": 0.0},
                "object_gid": {"reason": "not_selected", "score": 0.0},
            },
            "fkef": {
                "bid_price_for_seller": {"reason": "not_selected", "score": 0.0},
                "object_gid": {"reason": "not_selected", "score": 1.0},
            },
        }

    def test_pinned_obf_field_is_included_even_when_not_live(
        self, runtime_data_store: RuntimeDataStore
    ) -> None:
        non_obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="ExchangeBidPriceEvent",
            fields=[
                dump_field(
                    "average_price_",
                    "AveragePrice",
                    32,
                    FieldCategoryEnum.NUMBER,
                    proto_decl_order=0,
                ),
                dump_field(
                    "bid_price_for_seller_",
                    "BidPriceForSeller",
                    40,
                    FieldCategoryEnum.MESSAGE,
                    proto_decl_order=1,
                ),
                dump_field("object_gid_", "ObjectGid", 48, FieldCategoryEnum.NUMBER, proto_decl_order=2),
            ],
        )
        obf_message = DumpCSMessage(
            file_descriptor="GameReflection",
            name="jev",
            fields=[
                dump_field("fkdq", "fkdq", 32, FieldCategoryEnum.NUMBER),
                dump_field("fkdt", "fkdt", 40, FieldCategoryEnum.MESSAGE),
                dump_field("fkdu", "fkdu", 48, FieldCategoryEnum.NUMBER),
            ],
        )
        non_obf_sig = message_signature(
            "Com.Ankama.Dofus.Server.Game.Protocol.Exchange.ExchangeBidPriceEvent",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(32, NUMBER_SHAPE),
                field_signature(40, MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset(
                {FieldKey(32, "average_price_"), FieldKey(40, "bid_price_for_seller_")}
            ),
            dump_cs_msg=non_obf_message,
        )
        obf_sig = message_signature(
            "jev",
            declared_field_signatures=[
                declared_field_signature(NUMBER_SHAPE),
                declared_field_signature(MESSAGE_SHAPE),
            ],
            field_signatures=[
                field_signature(32, NUMBER_SHAPE),
                field_signature(40, MESSAGE_SHAPE),
            ],
            live_field_keys=frozenset({FieldKey(32, "fkdq"), FieldKey(40, "fkdt")}),
            dump_cs_msg=obf_message,
        )

        result = build_field_mapping_for_test(
            non_obf_signature=non_obf_sig,
            obf_signature=obf_sig,
            non_obf_messages_by_cls=build_message_lookup([non_obf_message]),
            obf_messages_by_cls=build_message_lookup([obf_message]),
            field_mapping_context=make_field_mapping_context(runtime_data_store),
            pinned_pair=PinnedPair(
                obf="jev",
                non_obf="Com.Ankama.Dofus.Server.Game.Protocol.Exchange.ExchangeBidPriceEvent",
                field_mapping_by_obf={"fkdu": "object_gid"},
            ),
        )

        assert result.field_mapping == {
            "fkdq": "average_price",
            "fkdt": "bid_price_for_seller",
            "fkdu": "object_gid",
        }
        assert result.field_mapping_unmapped_non_obf_fields == {}
