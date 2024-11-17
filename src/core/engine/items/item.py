from enum import IntEnum

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.enums.item_enum import ItemEnum
from D3Database.models.datas.items_root import ItemsRootItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.engine.fights.effect import EffectActionEnum


def is_weapon_hunter(object: ObjectItemInventory):
    return any(
        effect.action == EffectActionEnum.WEAPON_HUNTER
        for effect in object.item.effects
    )


def is_exchangeable_item(item: ItemsRootItem):
    return (item.m_flags & 8) != 0


class SetPositionEnum(IntEnum):
    COIFFE = 6
    CAPE = 7
    ARME = 1
    BOUCLIER = 15
    AMU = 0
    ANNEAU_1 = 2
    ANNEAU_2 = 4
    CEINTURE = 3
    BOTTES = 5


GATHERER_ITEM_GIDS: set[int] = {
    harvestable
    for sub_area in DataReader().sub_area_by_id.values()
    for harvestable in sub_area.harvestables
    if harvestable in DataReader().item_by_id
} | {ItemEnum.WATER}


GATHERED_ITEM_ID_BY_NAME = {
    I18N()
    .name_by_id[DataReader().item_by_id[item_id].nameId or 0]
    .lower()
    .replace("s", "")
    .replace(" ", ""): item_id
    for item_id in GATHERER_ITEM_GIDS
}
