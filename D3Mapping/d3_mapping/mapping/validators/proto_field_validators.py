from functools import cache
from typing import Any, Callable

from data_center.data_reader import DataReader
from enums.jobs_enum import HARVESTER_JOB_IDS
from pydantic import BaseModel

from d3_mapping.controller.data_center_controller import DataCenterController
from d3_mapping.controller.instancied_msg_info_controller import (
    MSG_INFO_BY_NAME,
    InstanciedMessageInfoController,
)
from d3_mapping.resources.protos.game.teleportation_pb2 import Teleporter
from D3Database.data_center.i18n import I18N
from D3Database.grid.directions import DirectionsEnum
from D3Database.grid.map_point import MAP_POINT_BY_CELL_ID, MapPoint


class ProtoFieldValidator(BaseModel):
    validators: list[Callable[[Any], bool]]


def is_defined(value: Any):
    return value is not None


def is_valid_tab_number(value: Any):
    return value > 0 and value <= 10


def is_valid_cell_id(value: Any):
    return value in MAP_POINT_BY_CELL_ID


def is_valid_cell_x(value: Any):
    return value in DataCenterController.POSSIBLE_COORD_X


def is_valid_cell_y(value: Any):
    return value in DataCenterController.POSSIBLE_COORD_Y


def is_valid_cells(value: Any):
    return all(is_valid_cell_id(cell) for cell in value)


def is_valid_world_x_coodinates(value: Any):
    return value in DataCenterController.get_all_x_world_coodinates()


def is_valid_world_y_coodinates(value: Any):
    return value in DataCenterController.get_all_y_world_coodinates()


def is_valid_map_id(value: Any):
    return value in DataCenterController.get_all_map_ids()


def is_valid_sub_area_id(value: Any):
    return value in DataCenterController.get_all_sub_area_ids()


def is_valid_direction(value: Any):
    return value in DirectionsEnum


def is_valid_skill_id(value: Any):
    return value in DataCenterController.get_all_skill_ids()


def is_valid_name_id_optional(value: Any):
    return value in I18N().name_by_id or value == 0


def is_0(value: Any):
    return value == 0


def is_valid_element_state(value: Any):
    return value in DataCenterController.POSSIBLE_ELEMENT_STATES


def is_valid_characteristic_id(value: Any):
    return value >= 0 and value <= 200
    return value in DataCenterController.get_all_characteristic_ids()


def is_valid_instance(value: Any):
    return value >= 0 and value < 100


def is_valid_positive(value: Any):
    return value >= 0


def is_valid_cooldown_spell(value: Any):
    return value >= 0 and value <= 10


def is_one(value: Any):
    return value == 1


def is_valid_negative(value: Any):
    return value < 0


def is_valid_strict_positive(value: Any):
    return value > 0


def is_valid_list_positive(value: list):
    return all([is_valid_positive(elem) for elem in value])


def is_valid_gid(value: Any):
    return value in DataCenterController.get_all_item_ids()


def is_valid_monster_gid(value: Any):
    return value in DataCenterController.get_all_monster_gids()


def is_valid_job_id(value: Any):
    return value in DataCenterController.get_all_job_ids()


def is_valid_job_lvl(value: Any):
    return value >= 0 and value <= 200


def is_valid_key_cells(value: Any):
    return all(
        key_cell in DataCenterController.get_all_key_cells() for key_cell in value
    )


def is_valid_amount_of_kamas(value: Any):
    return value <= 100_000_000 and value >= 0


def is_valid_sale_hotel_quantity(value: Any):
    return value in [1, 10, 100, 1000]


def is_valid_sale_hotel_quantities(value: Any):
    return all(is_valid_sale_hotel_quantity(elem) for elem in value)


def is_valid_position(value: Any):
    return value < 10_000


def is_destination_type_zaap(value: Any):
    return value == Teleporter.TELEPORTER_ZAAP


def is_valid_positive_total_quantity(value: Any):
    return value >= 0 and value < 10_000_000


def is_valid_total_quantity(value: Any):
    return value > -10_000_000 and value < 10_000_000


def is_valid_type_item(value: Any):
    return value > 0 and value < 1000
    return value in DataCenterController.get_all_type_item_ids()


def is_valid_spell(value: Any):
    return value in DataCenterController.get_all_spell_ids()


def is_valid_spell_lvl(value: Any):
    return value in DataCenterController.get_all_spell_lvl_ids()


def is_valid_spell_numero(value: Any):
    return value in DataCenterController.SPELL_NUMEROS


def is_valid_type_items(value: Any):
    return all(is_valid_type_item(elem) for elem in value)


def is_valid_tax_percentage(value: Any):
    return value == 2.0


def is_valid_tax_update_percentage(value: Any):
    return value == 1.0


def is_valid_max_item_lvl(value: Any):
    return value in [200, 60]


def is_valid_max_item_per_account(value: Any):
    return value >= 1 and value <= (201 + 200 * 5)


def is_valid_unsold_delay(value: Any):
    return value <= 24 * 28


def is_valid_unsold_delay_second(value: Any):
    return value >= 0 and value <= 60 * 60 * 24 * 28


def is_valid_age_bonus(value: Any):
    return value >= 0 and value <= 100


def is_valid_action_id(value: Any):
    return value >= 0 and value <= 500


def is_valid_npc_id(value: Any):
    return value in DataReader().npc_by_id or value < 0


def is_valid_npc_action_id(value: Any):
    return value in DataReader().npc_action_by_id


def is_valid_inventory_weight(value: Any):
    return value >= 0 and value <= 50_000


def is_valid_grade(value: Any):
    return value >= 0 and value <= 5


def is_valid_monster_level(value: Any):
    return value >= 1 and value <= 500


def is_valid_request_type_url(value: Any):
    return type(value) is str and value.endswith("Request")


def is_valid_event_type_url(value: Any):
    return type(value) is str and value.endswith("Event")


def is_not_default_value(value: Any):
    return value not in [{}, [], None, 0, False, ""]


def is_condition_respected(
    msg_namespace: str, field_name: str, field_validator: ProtoFieldValidator
) -> bool:
    if msg_namespace not in MSG_INFO_BY_NAME:
        return True
    for obf_msg_info in MSG_INFO_BY_NAME[msg_namespace].obf_msg_info:
        for validator in field_validator.validators:
            try:
                is_valid = validator(obf_msg_info.value_by_field_array.get(field_name))
                if not is_valid:
                    return False
            except Exception:
                return False
    return True


def is_not_always_default_value(msg_name: str, field_name: str) -> bool:
    return any(
        obf_msg_info.value_by_field_array[field_name]
        not in [{}, [], None, 0, False, ""]
        for obf_msg_info in MSG_INFO_BY_NAME[msg_name].obf_msg_info
    )


DEFAULT_PROTO_VALUES = [{}, [], None, 0, False, ""]


@cache
def get_count_defined_msg_field_values(msg_namespace: str, field_name: str) -> int:
    if msg_namespace not in MSG_INFO_BY_NAME:
        return 0
    unique_values = set()
    is_probably_dict_or_list: bool = True
    for obf_msg_info in MSG_INFO_BY_NAME[msg_namespace].obf_msg_info:
        if (
            field_name not in obf_msg_info.value_by_field_array
            or (value := obf_msg_info.value_by_field_array[field_name])
            in DEFAULT_PROTO_VALUES
        ):
            continue
        if is_probably_dict_or_list and (type(value) is list or type(value) is dict):
            return len(MSG_INFO_BY_NAME[msg_namespace].obf_msg_info)
        is_probably_dict_or_list = False
        unique_values.add(value)
    return len(unique_values)


def is_parsed_obf_msg(obf_msg_namespace: str):
    return obf_msg_namespace in MSG_INFO_BY_NAME


VALIDATORS_ON_FIELD: dict[str, dict[str, ProtoFieldValidator]] = {
    "CarryCharacter": {"cell": ProtoFieldValidator(validators=[is_valid_cell_id])},
    "ThrowCharacter": {"cell": ProtoFieldValidator(validators=[is_valid_cell_id])},
    "CharacterCharacteristics": {
        "experience": ProtoFieldValidator(validators=[is_valid_positive]),
        "experience_level_floor": ProtoFieldValidator(validators=[is_valid_positive]),
        "experience_next_level_floor": ProtoFieldValidator(
            validators=[is_valid_positive]
        ),
        "experience_bonus_limit": ProtoFieldValidator(validators=[is_valid_positive]),
        "kamas": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "SpellModifier": {"spell_id": ProtoFieldValidator(validators=[is_valid_spell])},
    "BidItem": {
        "quantity": ProtoFieldValidator(validators=[is_valid_positive_total_quantity]),
        "gid": ProtoFieldValidator(validators=[is_valid_gid]),
        "uid": ProtoFieldValidator(validators=[is_valid_strict_positive]),
    },
    "ExchangeBidHouseSearchRequest": {
        "object_gid": ProtoFieldValidator(validators=[is_valid_gid])
    },
    "ExchangeBidPriceEvent": {
        "object_gid": ProtoFieldValidator(validators=[is_valid_gid]),
        "average_price": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "SellingConditions": {
        "quantities": ProtoFieldValidator(validators=[is_valid_sale_hotel_quantities]),
        "types": ProtoFieldValidator(validators=[is_valid_type_items]),
        "tax_percentage": ProtoFieldValidator(validators=[is_valid_tax_percentage]),
        "tax_modification_percentage": ProtoFieldValidator(
            validators=[is_valid_tax_update_percentage]
        ),
        "max_item_level": ProtoFieldValidator(validators=[is_valid_max_item_lvl]),
        "max_item_per_account": ProtoFieldValidator(
            validators=[is_valid_max_item_per_account]
        ),
        "unsold_delay": ProtoFieldValidator(validators=[is_valid_unsold_delay]),
    },
    "ExchangeStartedWithMultiTabStorageEvent": {
        "tab_number": ProtoFieldValidator(validators=[is_valid_tab_number])
    },
    "GuildChestTabSelectRequest": {
        "tab_number": ProtoFieldValidator(validators=[is_valid_tab_number])
    },
    "MapMovementCancelRequest": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])
    },
    "MapMovementEvent": {
        "cells": ProtoFieldValidator(validators=[is_valid_cells]),
        "direction": ProtoFieldValidator(validators=[is_valid_direction]),
    },
    "MapChangeRequest": {"map_id": ProtoFieldValidator(validators=[is_valid_map_id])},
    "MapCurrentEvent": {"map_id": ProtoFieldValidator(validators=[is_valid_map_id])},
    "MapMovementRequest": {
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id]),
        "key_cells": ProtoFieldValidator(validators=[is_valid_key_cells]),
    },
    "MapInformationRequest": {
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id])
    },
    "FightMapInformationEvent": {
        "subarea_id": ProtoFieldValidator(validators=[is_valid_sub_area_id]),
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id]),
    },
    "MapCoordinates": {
        "world_x": ProtoFieldValidator(validators=[is_valid_world_x_coodinates]),
        "world_y": ProtoFieldValidator(validators=[is_valid_world_y_coodinates]),
    },
    "MapTeleportOnSameEvent": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])
    },
    "MapMovementRefusedEvent": {
        "cell_x": ProtoFieldValidator(validators=[is_valid_cell_x]),
        "cell_y": ProtoFieldValidator(validators=[is_valid_cell_y]),
    },
    "EntityDisposition": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])
    },
    "InteractiveElement": {
        "skill_id": ProtoFieldValidator(validators=[is_valid_skill_id]),
        "age_bonus": ProtoFieldValidator(validators=[is_valid_age_bonus]),
        "element_id": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "InteractiveElementSkill": {
        "skill_id": ProtoFieldValidator(validators=[is_valid_skill_id]),
        "skill_instance_uid": ProtoFieldValidator(
            validators=[is_valid_strict_positive]
        ),
        "name_id": ProtoFieldValidator(validators=[is_valid_name_id_optional]),
    },
    "StatedElement": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id]),
        "state": ProtoFieldValidator(validators=[is_valid_element_state]),
    },
    "FightStartingPositions": {
        "challengers_positions": ProtoFieldValidator(validators=[is_valid_cells]),
        "defenders_positions": ProtoFieldValidator(validators=[is_valid_cells]),
    },
    "ObjectItemInventory": {
        "position": ProtoFieldValidator(validators=[is_valid_positive])
    },
    "ObjectItem": {
        "quantity": ProtoFieldValidator(validators=[is_valid_positive_total_quantity]),
        "gid": ProtoFieldValidator(validators=[is_valid_gid]),
        "uid": ProtoFieldValidator(validators=[is_valid_strict_positive]),
    },
    "ObjectUidWithQuantity": {
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
        "quantity": ProtoFieldValidator(validators=[is_valid_total_quantity]),
    },
    "ObjectDeletedEvent": {
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive])
    },
    "ObjectsDeletedEvent": {
        "objects_uid": ProtoFieldValidator(validators=[is_valid_list_positive])
    },
    "JobExperience": {
        "job_id": ProtoFieldValidator(validators=[is_valid_job_id]),
        "job_level": ProtoFieldValidator(validators=[is_valid_job_lvl]),
        "job_xp": ProtoFieldValidator(validators=[is_valid_positive]),
        "job_xp_level_floor": ProtoFieldValidator(validators=[is_valid_positive]),
        "job_xp_next_level_floor": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "CharacterCharacteristic": {
        "characteristic_id": ProtoFieldValidator(
            validators=[is_valid_characteristic_id]
        )
    },
    "InteractiveUsedEvent": {
        "skill_id": ProtoFieldValidator(validators=[is_valid_skill_id])
    },
    "InteractiveUseEndedEvent": {
        "skill_id": ProtoFieldValidator(validators=[is_valid_skill_id])
    },
    "FightPlacementPositionRequest": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id]),
        "entity_id": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "StorageTab": {"tab_number": ProtoFieldValidator(validators=[is_valid_tab_number])},
    "NpcGenericActionRequest": {
        "npc_map_id": ProtoFieldValidator(validators=[is_valid_map_id]),
        "npc_id": ProtoFieldValidator(validators=[is_valid_npc_id]),
        "npc_action_id": ProtoFieldValidator(validators=[is_valid_npc_action_id]),
    },
    "NpcDialogQuestionEvent": {
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id])
    },
    "ExchangeSellRequest": {
        "quantity": ProtoFieldValidator(validators=[is_valid_positive_total_quantity]),
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ExchangeObjectMoveRequest": {
        "quantity": ProtoFieldValidator(validators=[is_valid_total_quantity]),
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ExchangeObjectAdded": {
        "quantity": ProtoFieldValidator(validators=[is_valid_total_quantity]),
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ObjectAddedEvent": {"object": ProtoFieldValidator(validators=[is_defined])},
    "ObjectAveragePricesEvent": {
        "object_gid": ProtoFieldValidator(validators=[is_valid_gid]),
        "average_price": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ExchangeStartedWithStorageEvent": {
        "storage_max_slot": ProtoFieldValidator(validators=[is_valid_positive])
    },
    "InventoryWeightEvent": {
        "inventory_weight": ProtoFieldValidator(validators=[is_valid_inventory_weight]),
        "weight_max": ProtoFieldValidator(validators=[is_valid_inventory_weight]),
    },
    "InventoryContentEvent": {
        "kamas": ProtoFieldValidator(validators=[is_valid_amount_of_kamas])
    },
    "ExchangeTypesItemsExchangerDescriptionForUserEvent": {
        "object_gid": ProtoFieldValidator(validators=[is_valid_gid])
    },
    "InteractiveUseRequest": {
        "element_id": ProtoFieldValidator(validators=[is_valid_positive]),
        "skill_instance_uid": ProtoFieldValidator(
            validators=[is_valid_strict_positive]
        ),
        "specific_instance_id": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ExchangeBidHousePriceRequest": {
        "object_gid": ProtoFieldValidator(validators=[is_valid_gid])
    },
    "ExchangeObjectModifyPricedRequest": {
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
        "quantity": ProtoFieldValidator(validators=[is_valid_sale_hotel_quantity]),
        "price": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "HavenBagEnterRequest": {
        "owner": ProtoFieldValidator(validators=[is_valid_positive])
    },
    "Element": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id]),
        "orientation": ProtoFieldValidator(validators=[is_valid_direction]),
    },
    "TeleportRequest": {
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id]),
        "destination_type": ProtoFieldValidator(validators=[is_destination_type_zaap]),
    },
    "SequenceEndEvent": {
        "action_id": ProtoFieldValidator(validators=[is_valid_action_id]),
    },
    "GameActionFightCastRequest": {
        "spell_id": ProtoFieldValidator(validators=[is_valid_spell]),
        "cell": ProtoFieldValidator(validators=[is_valid_cell_id]),
    },
    "MapObstacle": {"cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])},
    "SpellItem": {
        "spell_id": ProtoFieldValidator(validators=[is_valid_spell]),
        "spell_level": ProtoFieldValidator(validators=[is_valid_spell_numero]),
    },
    "GameActionAcknowledgementRequest": {
        "action_id": ProtoFieldValidator(validators=[is_valid_action_id])
    },
    "ExchangeObjectMovePricedRequest": {
        "object_uid": ProtoFieldValidator(validators=[is_valid_positive]),
        "quantity": ProtoFieldValidator(validators=[is_valid_sale_hotel_quantity]),
        "price": ProtoFieldValidator(validators=[is_valid_amount_of_kamas]),
    },
    "ExchangeBidHouseItemAddedEvent": {
        "price": ProtoFieldValidator(validators=[is_valid_amount_of_kamas]),
        "unsold_delay": ProtoFieldValidator(validators=[is_valid_unsold_delay_second]),
    },
    "ObjectQuantityEvent": {"object": ProtoFieldValidator(validators=[is_defined])},
    "MonsterInGroupInformation": {
        "gid": ProtoFieldValidator(validators=[is_valid_monster_gid]),
        "creature_grade": ProtoFieldValidator(validators=[is_valid_grade]),
        "level": ProtoFieldValidator(validators=[is_valid_monster_level]),
    },
    "LifePointsGain": {
        "delta": ProtoFieldValidator(validators=[is_valid_strict_positive])
    },
    "LifePointsLost": {
        "loss": ProtoFieldValidator(validators=[is_valid_strict_positive])
    },
    "UpdateLifePointsEvent": {
        "life_point": ProtoFieldValidator(validators=[is_valid_positive]),
        "max_life_point": ProtoFieldValidator(validators=[is_valid_strict_positive]),
    },
    "MonsterFighter": {
        "monster_gid": ProtoFieldValidator(validators=[is_valid_monster_gid]),
        "creature_grade": ProtoFieldValidator(validators=[is_valid_grade]),
    },
    "GameActionFightCastOnTargetRequest": {
        "spell_id": ProtoFieldValidator(validators=[is_valid_spell])
    },
    "Slide": {
        "start_cell": ProtoFieldValidator(validators=[is_valid_cell_id]),
        "end_cell": ProtoFieldValidator(validators=[is_valid_cell_id]),
    },
    "TeleportOnSameMap": {
        "cell": ProtoFieldValidator(validators=[is_valid_cell_id]),
    },
    "ExchangePositions": {
        "caster_cell_id": ProtoFieldValidator(validators=[is_valid_cell_id]),
        "target_cell_id": ProtoFieldValidator(validators=[is_valid_cell_id]),
    },
    "SpellCoolDownVariation": {
        "spell_id": ProtoFieldValidator(validators=[is_valid_spell]),
        "value": ProtoFieldValidator(validators=[is_valid_cooldown_spell]),
    },
    "SpellImmunity": {"spell_id": ProtoFieldValidator(validators=[is_valid_spell])},
    "InvisibleDetected": {"cell": ProtoFieldValidator(validators=[is_valid_cell_id])},
    "SpellsEvent": {
        "human_spells": ProtoFieldValidator(validators=[is_not_default_value])
    },
    "CharacterCharacteristicDetailedUsable": {
        "used": ProtoFieldValidator(validators=[is_valid_positive]),
        "base": ProtoFieldValidator(validators=[is_valid_positive]),
    },
    "ObjectEffect": {"value_int": ProtoFieldValidator(validators=[is_valid_positive])},
}


def validator_update_life_points_event(values: dict[str, Any]):
    if values["max_life_points"] < values["life_points"]:
        return False
    return True


def validator_inventory_weight_event(values: dict[str, Any]):
    # sometimes we can be overload (after a fight for example, so lets add offset juste for that)
    if values["weight_max"] + 30 <= values["inventory_weight"]:
        return False
    return True


def validator_character_characteristic_upgrade_request(values: dict[str, Any]):
    return not any(
        value >= values["chance"]
        for key, value in values.items()
        if key not in ["chance"]
    )


def validator_character_characteristic_detailed_usable(values: dict[str, Any]):
    if (
        values["used"]
        > values["additional"]
        + values["objects_and_mount_bonus"]
        + values["alignment_gift_bonus"]
        + values["temporary"]
        + values["base"]
    ):
        return False
    return True


def validator_exchange_started_with_pods_event(values: dict[str, Any]):
    if values["first_character_max_weight"] < values["first_character_current_weight"]:
        return False

    if (
        values["second_character_max_weight"]
        < values["second_character_current_weight"]
    ):
        return False

    return True


def global_validator_map_complementary_information_event(
    values_array: list[dict[str, Any]],
):
    count_off = 0
    count_on = 0
    for values in values_array:
        off_element_ids: list[int] = []
        on_element_ids: list[int] = []
        for interactive_element in values["interactive_elements"]:
            for disabled_skill in interactive_element.get("disabled_skills", []):
                skill = DataReader().skill_by_id[disabled_skill["skill_id"]]
                job_id = skill.parentJobId
                if (
                    job_id in HARVESTER_JOB_IDS
                    and skill.levelMin == 1
                    and interactive_element.get("on_current_map", False) is True
                ):
                    off_element_ids.append(interactive_element["element_id"])

            for enabled_skill in interactive_element.get("enabled_skill", []):
                skill = DataReader().skill_by_id[enabled_skill["skill_id"]]
                job_id = skill.parentJobId
                if (
                    job_id in HARVESTER_JOB_IDS
                    and skill.levelMin == 1
                    and interactive_element.get("on_current_map", False) is True
                ):
                    on_element_ids.append(interactive_element["element_id"])

        for stated_element in values["stated_elements"]:
            if (
                "element_id" in stated_element
                and stated_element["element_id"] in off_element_ids
                and stated_element["state"] == 0
            ):
                if stated_element["element_id"] in off_element_ids:
                    count_off += 1

                if stated_element["element_id"] in on_element_ids:
                    count_on += 1

    return count_on >= count_off


def validator_game_message(values: dict[str, Any]):
    if values.get("request") is not None and "content" in values["request"]:
        related_msg_name = values["request"]["content"]["type_url"].split(".")[-1]
        return "Response" not in related_msg_name and "Event" not in related_msg_name
    if values.get("event") is not None and "content" in values["event"]:
        related_msg_name = values["event"]["content"]["type_url"].split(".")[-1]
        return "Response" not in related_msg_name and "Request" not in related_msg_name
    return True


def validator_game_action_fight_event(values: dict[str, Any]):
    if values["source_id"] < 0:
        return True
    if not any(
        is_not_default_value(values[action])
        for action in [
            "slide",
            "life_points_lost",
            "life_points_gain",
            "death",
            "targeted_ability",
            "exchange_positions",
            "summons",
            "removable_effect",
            "modify_effects_duration",
            "spell_cool_down_variation",
            "tackled",
            "points_variation",
            "execute_script",
            "invisible_detected",
            "spell_remove",
        ]
    ):
        return False
    return True


def global_validator_entity_disposition(values_array: list[dict[str, Any]]):
    carrying_character_id_count: int = 0
    entity_id_count = 0
    for values in values_array:
        carrying_character_id_count += values["carrying_character_id"]
        entity_id_count += values["entity_id"]
    return entity_id_count >= carrying_character_id_count


def global_validator_object_with_quantity(values_array: list[dict[str, Any]]):
    object_uid_total: int = 0
    quantity_total: int = 0
    for values in values_array:
        object_uid_total += values["object_uid"]
        quantity_total += values["quantity"]
    return object_uid_total > quantity_total


def global_validator_interactive_element(values_array: list[dict[str, Any]]):
    element_type_id: int = 0
    element_id: int = 0
    for values in values_array:
        element_type_id += values["element_type_id"]
        element_id += values["element_id"]
    return element_id >= element_type_id


def global_validator_object_item(values_array: list[dict[str, Any]]):
    uid_total: int = 0
    quantity_total: int = 0
    for values in values_array:
        uid_total += values["uid"]
        quantity_total += values["quantity"]
    return uid_total >= quantity_total


def global_validator_element_with_instance_uid(values_array: list[dict[str, Any]]):
    uid_total: int = 0
    element_id_total: int = 0
    for values in values_array:
        uid_total += values["skill_instance_uid"]
        element_id_total += values["element_id"]
    return element_id_total > uid_total


def validator_slide(values: dict[str, Any]):
    return (
        MapPoint.from_cell_id(values["start_cell"]).distance_to_map_point(
            MapPoint.from_cell_id(values["end_cell"])
        )
        < 10
    )


def validator_exchange_positions(values: dict[str, Any]):
    return (
        MapPoint.from_cell_id(values["caster_cell_id"]).distance_to_map_point(
            MapPoint.from_cell_id(values["target_cell_id"])
        )
        < 10
    )


VALIDATORS_ON_SET_FIELDS: dict[str, tuple[Callable[[dict[str, Any]], bool], int]] = {
    "Slide": (validator_slide, 1),
    "ExchangePositions": (validator_exchange_positions, 1),
    "GameMessage": (validator_game_message, 1),
    "UpdateLifePointsEvent": (validator_update_life_points_event, 1),
    "InventoryWeightEvent": (validator_inventory_weight_event, 1),
    "CharacterCharacteristicDetailedUsable": (
        validator_character_characteristic_detailed_usable,
        1,
    ),
    "CharacterCharacteristicUpgradeRequest": (
        validator_character_characteristic_upgrade_request,
        1,
    ),
    "ExchangeStartedWithPodsEvent": (validator_exchange_started_with_pods_event, 1),
}

VALIDATORS_GLOBAL_ON_SET_FIELDS: dict[
    str, tuple[Callable[[list[dict[str, Any]]], bool], int]
] = {
    # "MapComplementaryInformationEvent": (
    #     global_validator_map_complementary_information_event,
    #     3,
    # ),
    "ObjectUidWithQuantity": (global_validator_object_with_quantity, 1),
    "ObjectItem": (global_validator_object_item, 1),
    "ExchangeObjectModifyPricedRequest": (global_validator_object_with_quantity, 1),
    "ExchangeObjectMovePricedRequest": (global_validator_object_with_quantity, 1),
    "InteractiveUseRequest": (global_validator_element_with_instance_uid, 1),
    "InteractiveElement": (global_validator_interactive_element, 1),
    "EntityDisposition": (global_validator_entity_disposition, 1),
}


if __name__ == "__main__":
    temp = InstanciedMessageInfoController().get_msg_infos_by_name().root["ile"]
    # (190842880, {'ekzm': 112, 'ekzn': True, 'ekzl': 513972, 'ekzp': 0})
    # infos = [(190842880, 513972), (190843392, 513975)]
    # for map_id, element_id in infos:
    #     temp = MapReader().get_ref_data_by_element_id(map_id)
    #     # print(DataReader().skill_by_id[6].parentJobId)
    #     print(temp[element_id])
    #     map = DataReader().map_pos_by_map_id[map_id]
    #     print(map.posX, map.posY)
