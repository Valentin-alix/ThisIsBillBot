from enum import IntEnum

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.enums.item_enum import ItemEnum
from dofus_unity_reader.models.datas.items_root import ItemsRootItem


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
