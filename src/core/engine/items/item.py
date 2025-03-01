from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.game_constants.item import GATHERER_ITEM_GIDS
from dofus_unity_reader.models.datas.items_root import ItemsRootItem


def is_exchangeable_item(item: ItemsRootItem):
    return (item.m_flags & 8) != 0


GATHERED_ITEM_ID_BY_NAME = {
    I18N()
    .name_by_id[DataReader().item_by_id[item_id].nameId]
    .lower()
    .replace("s", "")
    .replace(" ", ""): item_id
    for item_id in GATHERER_ITEM_GIDS
}
