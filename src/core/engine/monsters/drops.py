from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from dofus_unity_reader.enums.type_item_enum import TypeItemEnum
from dofus_unity_reader.models.datas.monsters_root import MonsterDrop

from src.controller.sale_hotel import SaleHotelController
from src.core.engine.items.item import GATHERED_ITEM_ID_BY_NAME
from src.core.game_constants import Items, Monsters


def get_rare_gid_with_weight_from_protector_drop(
    drops: list[MonsterDrop],
    server_id: int = 1,
) -> tuple[int | None, float]:
    avg_price_by_gid = SaleHotelController().get_avg_price_by_gid(server_id)

    res_object_id: int | None = None
    weight: float = 0

    for drop in drops:
        description = (
            I18N()
            .name_by_id[DataReader().item_by_id[drop.objectId].descriptionId or 0]
            .lower()
            .replace("s", "")
        )
        if drop.objectId in Items.CUSTOM_GATHERER_BY_SAC:
            res_object_id = Items.CUSTOM_GATHERER_BY_SAC[drop.objectId]
        elif description.startswith("cet énorme"):
            cleaned_desc = "".join(description.replace(".", "").split(" ")[-4:])
            for item_name, item_gid in GATHERED_ITEM_ID_BY_NAME.items():
                if item_name in cleaned_desc:
                    res_object_id = item_gid
                    break
            else:
                continue

        weight += (
            drop.percentDropForGrade1 / 100 * avg_price_by_gid.get(drop.objectId, 1)
        )
    return res_object_id, weight


PROTECTOR_DROP_ITEM_IDS = {
    drop.objectId
    for race in Monsters.PROTECTOR_RACES
    for monster in DataReader().monsters_by_race[race]
    for drop in monster.drops
    if DataReader().item_by_id[drop.objectId].typeId
    not in [310, TypeItemEnum.PIERRE_BRUTE]
}
