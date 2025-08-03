from logging import Logger

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.dungeon_info import (
    PLAYABLE_DUNGEONS,
    DungeonInfo,
)
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.game_constants.item import ItemEnum, ItemTypeEnum

from src.core.config import DUNGEON_OFFSET_LVL
from src.core.engine.movements.map.map_tools import MapTools


def do_have_key_access_to_dungeon(
    dungeon_info: DungeonInfo,
    objects_by_uid: dict[int, ObjectItemInventory],
    logger: Logger,
):
    related_king_ring_item = next(
        object.item for object in objects_by_uid.values() if object.item.gid == ItemEnum.KEY_RING
    )
    related_item_key_ids = [
        item.id
        for item in DataReader().item_by_id.values()
        if item.nameId is not None
        and dungeon_info.key_name in I18N().name_by_id[item.nameId]
        and item.typeId == ItemTypeEnum.KEY
    ]
    if len(related_item_key_ids) == 0:
        logger.error(f"Wtf did not found related key for name {dungeon_info.name}")
        return False

    logger.info(f"related item keys id : {related_item_key_ids}")
    logger.info(f"keyring value_int : {[effect.value_int for effect in related_king_ring_item.effects]}")

    does_have_king_ring_related_key = any(
        effect.value_int in related_item_key_ids for effect in related_king_ring_item.effects
    )
    return does_have_king_ring_related_key


def get_valid_dungeon_infos(
    level: int,
    is_sub: bool,
    objects_by_uid: dict[int, ObjectItemInventory],
    logger: Logger,
):
    return [
        dungeon_info
        for dungeon_info in PLAYABLE_DUNGEONS
        if dungeon_info.dungeon.optimalPlayerLevel + DUNGEON_OFFSET_LVL < level
        and (is_sub or MapTools.is_map_allowed_for_unsub(dungeon_info.dungeon.entranceMapId))
        and do_have_key_access_to_dungeon(dungeon_info, objects_by_uid, logger)
    ]
