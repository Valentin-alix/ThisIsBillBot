from logging import Logger

from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.item import ItemEnum, ItemTypeEnum

from src.core.engine.dungeons.dungeon_info import DungeonInfo


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
