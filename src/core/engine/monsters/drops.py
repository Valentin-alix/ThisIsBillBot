from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Database.enums.type_item_enum import TypeItemEnum
from D3Database.models.datas.monsters_root import MonsterDrop
from src.controller.sale_hotel import SaleHotelController
from src.controller.speed_sell_score import SpeedSellScoreController
from src.core.engine.items.item import GATHERED_ITEM_ID_BY_NAME
from src.core.game_constants import (
    CUSTOM_GATHERER_ITEM_BY_SAC_GID,
    Monsters,
)


def get_rare_gid_with_weight_from_protector_drop(
    drops: list[MonsterDrop],
) -> tuple[int | None, float]:
    avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
    speed_sell_score_by_gid = SpeedSellScoreController().get_speed_sell_score_by_gid

    res_object_id: int | None = None
    weight: float = 0

    for drop in drops:
        description = (
            I18N()
            .name_by_id[DataReader().item_by_id[drop.objectId].descriptionId or 0]
            .lower()
            .replace("s", "")
        )
        if drop.objectId in CUSTOM_GATHERER_ITEM_BY_SAC_GID:
            res_object_id = CUSTOM_GATHERER_ITEM_BY_SAC_GID[drop.objectId]
        elif description.startswith("cet énorme"):
            cleaned_desc = "".join(description.replace(".", "").split(" ")[-4:])
            for item_name, item_gid in GATHERED_ITEM_ID_BY_NAME.items():
                if item_name in cleaned_desc:
                    res_object_id = item_gid
                    break
            else:
                continue

        weight += (
            drop.percentDropForGrade1
            / 100
            * avg_price_by_gid.get(drop.objectId, 1)
            * speed_sell_score_by_gid.get(drop.objectId, 1.0)
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
