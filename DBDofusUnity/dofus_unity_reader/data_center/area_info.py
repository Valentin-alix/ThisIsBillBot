from pydantic import BaseModel

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.i18n import I18N
from DBDofusUnity.dofus_unity_reader.game_constants.area import AreaEnum, SubAreaEnum
from DBDofusUnity.dofus_unity_reader.game_constants.waypoint_enum import WaypointEnum


class AreaInfo(BaseModel):
    area_id: int
    sub_area_id: int | None = None
    min_lvl: int = 1
    waypoint_map_id_needed: int | None = None
    weight_multiplier: float = 1.0

    def __str__(self) -> str:
        area_name = I18N().name_by_id[DataReader().area_by_id[self.area_id].nameId]
        if self.sub_area_id:
            sub_area_name = I18N().name_by_id[DataReader().sub_area_by_id[self.sub_area_id].nameId]
        else:
            sub_area_name = ""
        return f"{area_name} sub : {sub_area_name}"

    def __hash__(self) -> int:
        return (self.area_id, self.sub_area_id).__hash__()

    def __repr__(self) -> str:
        return super().__str__()


AREAS_UNSUB_WITH_WEIGHT: list[AreaInfo] = [
    AreaInfo(area_id=AreaEnum.INCARNAM, weight_multiplier=0.05),
    AreaInfo(area_id=AreaEnum.ASTRUB, min_lvl=10),
]
AREAS_SUB_WITH_WEIGHT: list[AreaInfo] = [
    *AREAS_UNSUB_WITH_WEIGHT,
    AreaInfo(area_id=AreaEnum.AMAKNA, min_lvl=50),
    AreaInfo(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LAKE,
        min_lvl=30,
    ),
    AreaInfo(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LITNEG,
        min_lvl=80,
    ),
    AreaInfo(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_FIELD,
        min_lvl=30,
    ),
    AreaInfo(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.DENT_PIERRE,
        min_lvl=111,
    ),
    AreaInfo(
        area_id=AreaEnum.KOALAK_MONTAIN,
        sub_area_id=SubAreaEnum.ENCHANTED_LAKE,
        min_lvl=39,
    ),
    AreaInfo(area_id=AreaEnum.FRIGOST, min_lvl=91, waypoint_map_id_needed=WaypointEnum.FRIGOST),
    AreaInfo(area_id=AreaEnum.PANDALA, min_lvl=91, waypoint_map_id_needed=WaypointEnum.PANDALA),
    AreaInfo(
        area_id=AreaEnum.OTOMAI,
        min_lvl=111,
        waypoint_map_id_needed=WaypointEnum.PANDALA,
    ),
]
