from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)
from dofus_unity_reader.game_constants.item import ItemEnum, ItemTypeEnum
from dofus_unity_reader.game_constants.monster import PROTECTOR_RACES
from dofus_unity_reader.models.datas.items_root import ItemsRootItem


def is_exchangeable_item(item: ItemsRootItem):
    return (item.m_flags & 8) != 0


def get_equipment_on_position(
    objects_by_uid: dict[int, ObjectItemInventory],
    position: CharacterInventoryPositionEnum,
) -> ObjectItemInventory | None:
    return next(
        (object for object in objects_by_uid.values() if object.position == position),
        None,
    )


GATHERER_ITEM_GIDS: set[int] = {
    harvestable
    for sub_area in DataReader().sub_area_by_id.values()
    for harvestable in sub_area.harvestables
    if harvestable in DataReader().item_by_id
} | {ItemEnum.WATER}


GATHERED_ITEM_ID_BY_NAME = {
    I18N()
    .name_by_id[DataReader().item_by_id[item_id].nameId]
    .lower()
    .replace("s", "")
    .replace(" ", ""): item_id
    for item_id in GATHERER_ITEM_GIDS
}

PROTECTOR_DROP_ITEM_IDS = {
    drop.objectId
    for race in PROTECTOR_RACES
    for monster in DataReader().monsters_by_race[race]
    for drop in monster.drops
    if DataReader().item_by_id[drop.objectId].typeId
    not in [ItemTypeEnum.EKLEME, ItemTypeEnum.PIERRE_BRUTE]
}
