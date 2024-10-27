from enums.area_enum import AreaEnum, SubAreaEnum

HARVESTER_WEIGHT_ACTION = 1.5
FIGHTER_WEIGHT_ACTION = 1

LVL_LIMIT_FOR_HARVEST = 10
KAMAS_LIMIT_FOR_HARVEST = 5_000

type AreaInfoWithWeight = tuple[dict[str, int | None], float, int]

AREAS_UNSUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    ({"area_id": AreaEnum.INCARNAM, "sub_area_id": None}, 1, 1),
    ({"area_id": AreaEnum.ASTRUB, "sub_area_id": None}, 5, 10),
]

AREAS_SUB_WITH_WEIGHT: list[AreaInfoWithWeight] = [
    *AREAS_UNSUB_WITH_WEIGHT,
    ({"area_id": AreaEnum.AMAKNA, "sub_area_id": None}, 30, 50),
    ({"area_id": AreaEnum.CANIA_PLAIN, "sub_area_id": SubAreaEnum.CANIA_LAKE}, 20, 30),
    (
        {"area_id": AreaEnum.CANIA_PLAIN, "sub_area_id": SubAreaEnum.CANIA_LITNEG},
        20,
        80,
    ),
    ({"area_id": AreaEnum.CANIA_PLAIN, "sub_area_id": SubAreaEnum.CANIA_FIELD}, 20, 30),
]
