from typing import Any, Callable


from D3Database.data_center.i18n import I18N
from d3_mapping.controller.data_center_controller import DataCenterController
from d3_mapping.controller.instancied_msg_info_controller import (
    MSG_INFO_BY_NAME,
)
from d3_mapping.mapping.validators.proto_field_validator import ProtoFieldValidator
from D3Database.grid.directions import DirectionsEnum
from D3Database.grid.map_point import MAP_POINT_BY_CELL_ID
from data_center.data_reader import DataReader


def is_defined(value: Any):
    return value is not None


def is_valid_tab_number(value: Any):
    return value > 0 and value <= 10


def is_valid_slot_spell(value: Any):
    return value >= 0 and value <= 100


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
    return value in [1, 10, 100]


def is_valid_sale_hotel_quantities(value: Any):
    return all(is_valid_sale_hotel_quantity(elem) for elem in value)


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


def is_not_default_value(value: Any):
    return value not in [{}, [], None, 0, False, ""]


def is_condition_respected(
    msg_namespace: str, field_name: str, field_validator: ProtoFieldValidator
) -> tuple[bool, Any]:
    if msg_namespace not in MSG_INFO_BY_NAME:
        return True, None
    for obf_msg_info in MSG_INFO_BY_NAME[msg_namespace].obf_msg_info:
        for validator in field_validator.validators:
            related_value = obf_msg_info.value_by_field_array.get(field_name)
            if not validator(related_value):
                return False, related_value
    return True, None


def is_not_always_default_value(msg_name: str, field_name: str) -> bool:
    return any(
        obf_msg_info.value_by_field_array[field_name]
        not in [{}, [], None, 0, False, ""]
        for obf_msg_info in MSG_INFO_BY_NAME[msg_name].obf_msg_info
    )


def get_count_msg_field_values(msg_namespace: str, field_name: str) -> int:
    if msg_namespace not in MSG_INFO_BY_NAME:
        return 0
    unique_values = set()
    for msg_info in MSG_INFO_BY_NAME[msg_namespace].obf_msg_info:
        value = msg_info.value_by_field_array.get(field_name, None)
        if isinstance(value, list) or isinstance(value, dict):
            return len(MSG_INFO_BY_NAME[msg_namespace].obf_msg_info)
        else:
            unique_values.add(value)
    return len(unique_values)


def is_parsed_obf_msg(obf_msg_name: str):
    return obf_msg_name in MSG_INFO_BY_NAME


VALIDATORS_ON_FIELD: dict[str, dict[str, ProtoFieldValidator]] = {
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
    "CharacterLifeStatusEvent": {
        "phoenix_map_id": ProtoFieldValidator(validators=[is_valid_map_id])
    },
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
    "MapExtendedCoordinates": {
        "world_x": ProtoFieldValidator(validators=[is_valid_world_x_coodinates]),
        "world_y": ProtoFieldValidator(validators=[is_valid_world_y_coodinates]),
        "map_id": ProtoFieldValidator(validators=[is_valid_map_id]),
        "sub_area_id": ProtoFieldValidator(validators=[is_valid_sub_area_id]),
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
    "ObjectUseOnCellRequest": {
        "cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])
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
    "TeleportRequest": {"map_id": ProtoFieldValidator(validators=[is_valid_map_id])},
    "SequenceEndEvent": {
        "action_id": ProtoFieldValidator(validators=[is_valid_action_id]),
    },
    "GameActionFightCastRequest": {
        "spell_id": ProtoFieldValidator(validators=[is_valid_spell]),
        "cell": ProtoFieldValidator(validators=[is_valid_cell_id]),
    },
    "MapObstacle": {"cell_id": ProtoFieldValidator(validators=[is_valid_cell_id])},
    "ShortcutBarSwapRequest": {
        "first_slot_id": ProtoFieldValidator(validators=[is_valid_slot_spell]),
        "second_slot_id": ProtoFieldValidator(validators=[is_valid_slot_spell]),
    },
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
    "InteractiveUseErrorEvent": {
        "element_id": ProtoFieldValidator(validators=[is_valid_positive]),
        "skill_instance_uid": ProtoFieldValidator(validators=[is_valid_positive]),
    },
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
        "value": ProtoFieldValidator(validators=[is_valid_positive]),
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
}


def validator_update_life_points_event(values: dict[str, Any]):
    if values["max_life_points"] < values["life_points"]:
        return False
    return True


def validator_inventory_weight_event(values: dict[str, Any]):
    if values["weight_max"] < values["inventory_weight"]:
        return False
    return True


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


VALIDATORS_ON_SET_FIELDS: dict[str, Callable[[dict[str, Any]], bool]] = {
    "UpdateLifePointsEvent": validator_update_life_points_event,
    "InventoryWeightEvent": validator_inventory_weight_event,
    "CharacterCharacteristicDetailedUsable": validator_character_characteristic_detailed_usable,
}
