from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_CELL_ID
from DBDofusUnity.datas.protos.non_obf.game.fight_pb2 import FightEndEvent
from DBDofusUnity.datas.protos.non_obf.game.guild_mission_pb2 import ServerMaintenanceEvent
from DBDofusUnity.datas.protos.non_obf.game.spell_pb2 import SpellVariantActivationEvent
from DBDofusUnity.proto_mapper_assembly.validators.global_validators import (
    global_validator_interactive_element,
)
from DBDofusUnity.proto_mapper_assembly.validators.field_validators import (
    VALIDATORS_ON_FIELD,
    is_non_empty_list_of,
    is_valid_action_id,
    is_valid_actor_id,
    is_valid_age_bonus,
    is_valid_amount_of_kamas,
    is_valid_bak_bid_action,
    is_valid_bak_bid_validation,
    is_valid_char_usable_base,
    is_valid_char_usable_context_mod,
    is_valid_char_usable_objects_bonus,
    is_valid_characteristic_id,
    is_valid_cooldown_spell,
    is_valid_craft_count,
    is_valid_date_iso,
    is_valid_direction,
    is_valid_duration,
    is_valid_grade,
    is_valid_inventory_weight,
    is_valid_latency_ms,
    is_valid_level,
    is_valid_max_item_lvl,
    is_valid_max_item_per_account,
    is_valid_monster_gid,
    is_valid_monster_level,
    is_valid_nickname,
    is_valid_position,
    is_valid_positive,
    is_valid_positive_quantity,
    is_valid_prefix,
    is_valid_sale_hotel_quantity,
    is_valid_strict_positive,
    is_valid_summon_grade,
    is_valid_tab_number,
    is_valid_tax_percentage,
    is_valid_tax_update_percentage,
    is_valid_timestamp,
    is_valid_total_quantity,
    is_valid_type_item,
    is_valid_unsold_delay,
    is_valid_unsold_delay_second,
)


class TestFieldValidators:
    def _sample_values(self) -> dict[str, int]:
        data_reader = DataReader()
        return {
            "cell_id": next(iter(MAP_POINT_BY_CELL_ID)),
            "skill_id": next(iter(data_reader.get_all_skill_ids())),
            "item_id": next(iter(data_reader.get_all_item_ids())),
            "monster_gid": next(iter(data_reader.get_all_monster_gids())),
            "job_id": next(iter(data_reader.get_all_job_ids())),
            "sub_area_id": next(iter(data_reader.get_all_sub_area_ids())),
            "map_id": next(iter(data_reader.get_all_map_ids())),
            "name_id": next(iter(I18N().name_by_id)),
            "spell_id": next(iter(data_reader.get_all_spell_ids())),
            "spell_level_id": next(iter(data_reader.get_all_spell_lvl_ids())),
            "npc_id": next(iter(data_reader.npc_by_id)),
            "npc_action_id": next(iter(data_reader.npc_action_by_id)),
            "x": next(iter(data_reader.POSSIBLE_COORD_X)),
            "y": next(iter(data_reader.POSSIBLE_COORD_Y)),
            "element_state": next(iter(data_reader.POSSIBLE_ELEMENT_STATES)),
            "spell_numero": next(iter(data_reader.SPELL_NUMEROS)),
            "key_cell": next(iter(data_reader.get_all_key_cells())),
            "world_x": next(iter(data_reader.get_all_x_world_coodinates())),
            "world_y": next(iter(data_reader.get_all_y_world_coodinates())),
        }

    def test_location_and_numeric_validators(self) -> None:
        assert is_valid_tab_number(1) is True
        assert is_valid_direction(next(iter(DirectionsEnum))) is True
        assert is_valid_characteristic_id(1) is True
        assert is_valid_positive(1) is True
        assert is_valid_cooldown_spell(3) is True
        assert is_valid_strict_positive(1) is True
        assert is_valid_amount_of_kamas(100) is True
        assert is_valid_sale_hotel_quantity(10) is True
        assert is_valid_position(42) is True
        assert is_valid_positive_quantity(100) is True
        assert is_valid_total_quantity(-1) is True
        assert is_valid_type_item(1) is True
        assert is_valid_action_id(10) is True
        assert is_valid_inventory_weight(100) is True
        assert is_valid_grade(1) is True
        assert is_valid_monster_level(10) is True
        assert is_valid_duration(12) is True
        assert is_valid_max_item_lvl(200) is True
        assert is_valid_max_item_per_account(1) is True
        assert is_valid_unsold_delay(10) is True
        assert is_valid_unsold_delay_second(10) is True
        assert is_valid_age_bonus(10) is True

    def test_text_and_identifier_validators(self) -> None:
        assert is_valid_prefix("abc") is True
        assert is_valid_nickname("Player") is True
        assert is_valid_date_iso("2024-01-01T00:00:00Z") is True
        assert is_valid_tax_percentage(2.0) is True
        assert is_valid_tax_update_percentage(1.0) is True
        assert is_valid_char_usable_base(6) is True
        assert is_valid_char_usable_objects_bonus(1) is True
        assert is_valid_char_usable_context_mod(-1) is True

    def test_invalid_value_paths(self) -> None:
        assert is_valid_nickname("a1") is False
        assert is_valid_prefix("a1") is False
        assert is_valid_date_iso("not-a-date") is False

    def test_non_empty_list_of_combines_container_and_item_validation(self) -> None:
        validator = is_non_empty_list_of(is_valid_strict_positive)

        assert validator([1, 2]) is True
        assert validator([]) is False
        assert validator([1, 0]) is False

    def test_new_validators(self) -> None:
        assert is_valid_level(1) is True
        assert is_valid_level(200) is True
        assert is_valid_level(0) is False
        assert is_valid_level(201) is False

        assert is_valid_timestamp(1) is True
        assert is_valid_timestamp(1_000_000_000) is True
        assert is_valid_timestamp(0) is False
        assert is_valid_timestamp(-1) is False

    def test_new_bot_message_scalar_validators(self) -> None:
        assert is_valid_craft_count(1) is True
        assert is_valid_craft_count(10_001) is False
        assert is_valid_latency_ms(123) is True
        assert is_valid_latency_ms(-1) is False

    def test_fight_end_validators_reject_swapped_runtime_values(self) -> None:
        field_validators = VALIDATORS_ON_FIELD[FightEndEvent]

        assert field_validators["duration"](39_188) is True
        assert field_validators["duration"](200) is False
        assert field_validators["duration"](-1) is False
        assert field_validators["reward_rate"](-1) is True
        assert field_validators["reward_rate"](100) is True
        assert field_validators["reward_rate"](101) is False
        assert field_validators["reward_rate"](39_188) is False
        assert field_validators["loot_share_limit_malus"](0) is True
        assert field_validators["loot_share_limit_malus"](120) is True
        assert field_validators["loot_share_limit_malus"](201) is False

    def test_bak_enum_validators_accept_numeric_and_named_values(self) -> None:
        assert is_valid_bak_bid_action(6) is True
        assert is_valid_bak_bid_action("BID_BUY_OGRINE") is True
        assert is_valid_bak_bid_action(0) is False
        assert is_valid_bak_bid_action("BID_INVALID_ACTION") is False
        assert is_valid_bak_bid_action(99) is False

        assert is_valid_bak_bid_validation(9) is True
        assert is_valid_bak_bid_validation("BID_VALIDATION_SUCCESS") is True
        assert is_valid_bak_bid_validation(99) is False

    def test_bot_message_field_validators_apply_semantic_constraints(self) -> None:
        sample_values = self._sample_values()

        assert VALIDATORS_ON_FIELD[SpellVariantActivationEvent]["spell_id"](sample_values["spell_id"]) is True
        assert VALIDATORS_ON_FIELD[ServerMaintenanceEvent]["maintenance_date"]("2026-09-01T05:00:00Z") is True
        assert VALIDATORS_ON_FIELD[ServerMaintenanceEvent]["maintenance_date"]("maintenance") is False

    def test_summon_runtime_sub_message_field_validators(self) -> None:
        sample_values = self._sample_values()

        assert is_valid_actor_id(-2) is True
        assert is_valid_actor_id(0) is False
        assert is_valid_monster_gid(sample_values["monster_gid"]) is True
        assert is_valid_monster_gid(0) is False
        assert is_valid_summon_grade(1) is True
        assert is_valid_summon_grade(0) is False
        assert is_valid_level(1) is True
        assert is_valid_level(0) is False


class TestGlobalValidators:
    def test_global_validator_interactive_element(self) -> None:
        assert global_validator_interactive_element([{"element_type_id": 1, "element_id": 2}]) is True
