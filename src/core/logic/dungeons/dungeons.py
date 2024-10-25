from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from src.core.logic.dungeons.consts import (
    DUNGEON_OFFSET_LVL,
    DUNGEONS_INFOS,
    KEY_RING_ITEM_ID,
)
from src.core.logic.dungeons.dungeon_info import DungeonInfo
from src.core.logic.map.map_tools import MapTools
from src.interfaces.enums.item_type_enum import ItemTypeEnum


def do_have_key_access_to_dungeon(
    dungeon_info: DungeonInfo, objects_by_uid: dict[int, ObjectItemInventory]
):
    related_king_ring_item = next(
        object.item
        for object in objects_by_uid.values()
        if object.item.gid == KEY_RING_ITEM_ID
    )
    related_item_key_ids = [
        item.id
        for item in DataReader().item_by_id.values()
        if item.nameId is not None
        and dungeon_info.key_name in I18N().name_by_id[item.nameId]
        and item.typeId == ItemTypeEnum.KEY
    ]
    if len(related_item_key_ids) == 0:
        print(f"Wtf did not found related key for name {dungeon_info.name}")

    does_have_king_ring_related_key = any(
        effect.value_int in related_item_key_ids
        for effect in related_king_ring_item.effects
    )
    return does_have_king_ring_related_key


def get_valid_dungeon_infos(
    level: int, is_sub: bool, objects_by_uid: dict[int, ObjectItemInventory]
):
    return [
        dungeon_info
        for dungeon_info in DUNGEONS_INFOS
        if dungeon_info.dungeon.optimalPlayerLevel + DUNGEON_OFFSET_LVL < level
        and (
            is_sub
            or MapTools.is_map_allowed_for_unsub(dungeon_info.dungeon.entranceMapId)
        )
        and do_have_key_access_to_dungeon(dungeon_info, objects_by_uid)
    ]


if __name__ == "__main__":
    values = [1569, 1570, 6884, 7309, 7310, 27404]
    related_item_key = [
        item
        for item in DataReader().item_by_id.values()
        if item.nameId is not None
        and "Clef des Champs" in I18N().name_by_id[item.nameId]
    ]
    dungeon = next(
        dungeon
        for dungeon in DataReader().dungeon_by_id.values()
        if "Tournesol Affamé".lower() in I18N().name_by_id[dungeon.nameId].lower()
        and len(dungeon.mapIds) > 2
    )
    print(dungeon.optimalPlayerLevel)
