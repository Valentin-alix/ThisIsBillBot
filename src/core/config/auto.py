from pydantic import BaseModel
from data_center.data_reader import DataReader
from data_center.i18n import I18N
from enums.area_enum import AreaEnum, SubAreaEnum
from enums.jobs_enum import JobEnum

LVL_LIMIT_FOR_HARVEST = 10
KAMAS_LIMIT_FOR_HARVEST = 10_000


class AreaInfoWithWeight(BaseModel):
    area_id: int
    sub_area_id: int | None = None
    weight: int = 1
    min_lvl: int = 1
    waypoint_id_needed: int | None = None
    min_job_lvls: dict[JobEnum, int] = {}

    def __str__(self) -> str:
        area_name = I18N().name_by_id[DataReader().area_by_id[self.area_id].nameId]
        if self.sub_area_id:
            sub_area_name = I18N().name_by_id[
                DataReader().sub_area_by_id[self.sub_area_id].nameId
            ]
        else:
            sub_area_name = ""
        return f"{area_name} sub : {sub_area_name}"

    def __repr__(self) -> str:
        return super().__str__()


AREAS_UNSUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    AreaInfoWithWeight(area_id=AreaEnum.INCARNAM),
    AreaInfoWithWeight(area_id=AreaEnum.ASTRUB, weight=5, min_lvl=10),
]

AREAS_SUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    *AREAS_UNSUB_WITH_WEIGHT,
    AreaInfoWithWeight(area_id=AreaEnum.AMAKNA, weight=40, min_lvl=50),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LAKE,
        weight=20,
        min_lvl=30,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_LITNEG,
        weight=20,
        min_lvl=80,
        min_job_lvls={JobEnum.WOODCUTTER: 100},
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.CANIA_FIELD,
        weight=20,
        min_lvl=30,
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.CANIA_PLAIN,
        sub_area_id=SubAreaEnum.DENT_PIERRE,
        weight=50,
        min_lvl=111,
        min_job_lvls={JobEnum.ALCHEMIST: 140, JobEnum.PEASANT: 180},
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.KOALAK_MONTAIN,
        sub_area_id=SubAreaEnum.ENCHANTED_LAKE,
        weight=30,
        min_lvl=39,
        min_job_lvls={JobEnum.WOODCUTTER: 150},
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.FRIGOST,
        weight=70,
        min_lvl=91,
        waypoint_id_needed=54172969,
        min_job_lvls={
            JobEnum.ALCHEMIST: 200,
            JobEnum.WOODCUTTER: 200,
        },
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.PANDALA,
        weight=60,
        min_lvl=91,
        waypoint_id_needed=207619076,
        min_job_lvls={
            JobEnum.ALCHEMIST: 120,
            JobEnum.WOODCUTTER: 190,
            JobEnum.PEASANT: 100,
            JobEnum.MINER: 100,
        },
    ),
    AreaInfoWithWeight(
        area_id=AreaEnum.OTOMAI,
        weight=60,
        min_lvl=111,
        waypoint_id_needed=207619076,
        min_job_lvls={
            JobEnum.ALCHEMIST: 160,
            JobEnum.PEASANT: 160,
            JobEnum.WOODCUTTER: 140,
        },
    ),
]
