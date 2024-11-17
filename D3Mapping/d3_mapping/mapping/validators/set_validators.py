from typing import Any, Callable

from D3Database.data_center.data_reader import DataReader
from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.mapping.validators.field_validators import (
    is_not_default_value,
    is_valid_sale_hotel_quantity,
)


def validator_game_message(values: dict[str, Any]):
    if values.get("request") is not None and "content" in values["request"]:
        related_msg_name = values["request"]["content"]["type_url"].split(".")[-1]
        return "Response" not in related_msg_name and "Event" not in related_msg_name
    if values.get("event") is not None and "content" in values["event"]:
        related_msg_name = values["event"]["content"]["type_url"].split(".")[-1]
        return "Response" not in related_msg_name and "Request" not in related_msg_name
    return True


def validator_update_life_points_event(values: dict[str, Any]):
    if values["max_life_points"] < values["life_points"]:
        return False
    return True


def validator_inventory_weight_event(values: dict[str, Any]):
    # sometimes we can be overload (after a fight for example, so lets add offset juste for that)
    if values["weight_max"] + 500 <= values["inventory_weight"]:
        return False
    return True


def validator_exchange_bid_seller_started_event(values: dict[str, Any]):
    for item_sale in values["items"]:
        if not is_valid_sale_hotel_quantity(item_sale["item"]["quantity"]):
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
            "spell_remove",
        ]
    ):
        return False
    return True


def validator_slide(values: dict[str, Any]):
    if values["start_cell"] == -1 and values["end_cell"] == -1:
        return True
    if values["start_cell"] == values["end_cell"]:
        return False
    return (
        MapPoint.from_cell_id(values["start_cell"]).distance_to_map_point(
            MapPoint.from_cell_id(values["end_cell"])
        )
        < 10
    )


def validator_exchange_positions(values: dict[str, Any]):
    if values["caster_cell_id"] == values["target_cell_id"]:
        return False
    return (
        MapPoint.from_cell_id(values["caster_cell_id"]).distance_to_map_point(
            MapPoint.from_cell_id(values["target_cell_id"])
        )
        < 10
    )


def validator_character_characteristic_detailed_usable(values: dict[str, Any]):
    if values["used"] < 0:
        return False
    if values["used"] > 12:
        return False
    if values["base"] < 3 or values["base"] > 12:
        return False
    if values["alignment_gift_bonus"] != 0:
        return False
    if values["additional"] != 0:
        return False
    if values["context_modification"] > 0:
        return False
    if values["used"] > values["base"] + values["objects_and_mount_bonus"]:
        return False
    return True


def validator_fight_refresh_character_stats_event(
    values: dict[str, Any],
):
    if values["fighter_id"] == 0:
        return False
    if values["fighter_id"] < 0:
        return True
    characteristics = values["stats"]["characteristics"]
    for characteristic in characteristics:
        if characteristic["characteristic_id"] != 1:
            continue
        characteristic_usable = characteristic["usable"]
        if characteristic_usable is None:
            continue
        if any(
            key not in characteristic_usable
            for key in [
                "temporary",
                "objects_and_mount_bonus",
                "alignment_gift_bonus",
                "used",
                "base",
                "additional",
                "context_modification",
            ]
        ):
            continue
        if (
            characteristic_usable["objects_and_mount_bonus"] < 0
            or characteristic_usable["objects_and_mount_bonus"] > 6
        ):
            return False
        if characteristic_usable["base"] not in [5, 6, 7]:
            return False
        if characteristic_usable["used"] < 0 or characteristic_usable["used"] > 12:
            return False
        if characteristic_usable["additional"] != 0:
            return False
        if characteristic_usable["temporary"] != 0:
            return False
        if characteristic_usable["alignment_gift_bonus"] != 0:
            return False
        if characteristic_usable["context_modification"] > 0:
            return False
        if (
            characteristic_usable["base"]
            + characteristic_usable["objects_and_mount_bonus"]
            > 12
        ):
            return False
        if (
            characteristic_usable["used"]
            > characteristic_usable["objects_and_mount_bonus"]
            + characteristic_usable["base"]
        ):
            return False
    return True


def validator_spells_event(values: dict[str, Any]):
    if len(values["human_spells"]) == 0:
        return False
    for spell in values["human_spells"]:
        if spell["spell_id"] not in DataReader().spell_by_id:
            return False
    return True


def validator_characteristic_detailed_usable(values: dict[str, Any]):
    if values["used"] > values["base"] + values["objects_and_mount_bonus"]:
        return False
    return True


VALIDATORS_ON_SET_FIELDS: dict[str, tuple[Callable[[dict[str, Any]], bool], int]] = {
    "Slide": (validator_slide, 1),
    "ExchangePositions": (validator_exchange_positions, 1),
    "GameMessage": (validator_game_message, 1),
    "UpdateLifePointsEvent": (validator_update_life_points_event, 1),
    "InventoryWeightEvent": (validator_inventory_weight_event, 1),
    "ExchangeStartedWithPodsEvent": (validator_exchange_started_with_pods_event, 1),
    "ExchangeBidSellerStartedEvent": (validator_exchange_bid_seller_started_event, 1),
    "FightRefreshCharacterStatsEvent": (
        validator_fight_refresh_character_stats_event,
        1,
    ),
    "SpellsEvent": (validator_spells_event, 1),
    "CharacterCharacteristicDetailedUsable": (
        validator_characteristic_detailed_usable,
        1,
    ),
}
