from data_center.data_reader import DataReader
from data_center.i18n import I18N
from enums.area_enum import AreaEnum, SubAreaEnum
from pydantic import BaseModel

DO_EXTRA_ACTION = True
DO_FIGHTER = True
DO_SALE_HOTEL = True
DO_CRAFT = False
DO_DUNGEON = False
DO_USE_GUILD_CHEST = True
DO_REGISTER_PRICE = False


LVL_LIMIT_FOR_HARVEST = 10
KAMAS_LIMIT_FOR_HARVEST = 5_000


class AreaInfoWithWeight(BaseModel):
    area_id: int
    sub_area_id: int | None = None
    min_lvl: int = 1
    waypoint_id_needed: int | None = None

    def __str__(self) -> str:
        area_name = I18N().name_by_id[DataReader().area_by_id[self.area_id].nameId]
        if self.sub_area_id:
            sub_area_name = I18N().name_by_id[
                DataReader().sub_area_by_id[self.sub_area_id].nameId
            ]
        else:
            sub_area_name = ""
        return f"{area_name} sub : {sub_area_name}"

    def __hash__(self) -> int:
        return (self.area_id, self.sub_area_id).__hash__()

    def __repr__(self) -> str:
        return super().__str__()


AREAS_UNSUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    AreaInfoWithWeight(area_id=AreaEnum.INCARNAM),
    AreaInfoWithWeight(area_id=AreaEnum.ASTRUB, min_lvl=10),
]

AREAS_SUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    *AREAS_UNSUB_WITH_WEIGHT,
    AreaInfoWithWeight(area_id=AreaEnum.AMAKNA, min_lvl=50),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LAKE,
        min_lvl=30,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LITNEG,
        min_lvl=80,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_FIELD,
        min_lvl=30,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.DENT_PIERRE,
        min_lvl=111,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.KOALAK_MONTAIN,
        sub_area_id=SubAreaEnum.ENCHANTED_LAKE,
        min_lvl=39,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.FRIGOST, min_lvl=91, waypoint_id_needed=54172969
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.PANDALA, min_lvl=91, waypoint_id_needed=207619076
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.OTOMAI,
        min_lvl=111,
        waypoint_id_needed=207619076,
    ),
]
