from typing import Any, Callable

from D3Database.data_center.data_reader import DataReader
from D3Database.enums.jobs_enum import HARVESTER_JOB_IDS


def global_validator_character_characteristic_upgrade_request(
    values_array: list[dict[str, Any]],
):
    values_chance_count = 0
    for value_array in values_array:
        is_not_maxed_chance = any(
            value >= value_array["chance"]
            for key, value in value_array.items()
            if key != "chance"
        )
        if not is_not_maxed_chance:
            values_chance_count += 1

    return values_chance_count >= len(values_array) / 4


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
    for values in values_array:
        if values["element_id"] > 800_000:
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


VALIDATORS_GLOBAL_ON_SET_FIELDS: dict[
    str, tuple[Callable[[list[dict[str, Any]]], bool], int]
] = {
    "MapComplementaryInformationEvent": (
        global_validator_map_complementary_information_event,
        3,
    ),
    "CharacterCharacteristicUpgradeRequest": (
        global_validator_character_characteristic_upgrade_request,
        1,
    ),
    "ObjectUidWithQuantity": (global_validator_object_with_quantity, 1),
    "ObjectItem": (global_validator_object_item, 1),
    "ExchangeObjectModifyPricedRequest": (global_validator_object_with_quantity, 1),
    "ExchangeObjectMovePricedRequest": (global_validator_object_with_quantity, 1),
    "InteractiveUseRequest": (global_validator_element_with_instance_uid, 1),
    "InteractiveElement": (global_validator_interactive_element, 1),
    "EntityDisposition": (global_validator_entity_disposition, 1),
}
