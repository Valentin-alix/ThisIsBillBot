from enums.area_enum import AreaEnum, SubAreaEnum
from pydantic import BaseModel

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


class AutoBotInfo(BaseModel):
    playtime_start: str
    playtime_end: str


SUICIDE_BOT_INFOS: dict[str, AutoBotInfo] = {
    # new
    "yolo.ezrealeu2+1747935351.2405686@outlook.fr": AutoBotInfo(
        playtime_start="04:00", playtime_end="20:00"
    ),
    # "yolo.ezrealeu2+1747935431.2478561@outlook.fr": SuicideBotInfo(
    #     playtime_start="04:00", playtime_end="12:00"
    # ),
    # end new
    # new
    # "yolo.ezrealeu2+1747935509.5774288@outlook.fr": SuicideBotInfo(
    #     playtime_start="12:00", playtime_end="20:00"
    # ),
    # "yolo.ezrealeu2+1747935591.7806125@outlook.fr": SuicideBotInfo(
    #     playtime_start="12:00", playtime_end="20:00"
    # ),
    # end new
    # new
    # "yolo.ezrealeu2+1747983370.305707@outlook.fr": SuicideBotInfo(
    #     playtime_start="20:00", playtime_end="04:00"
    # ),
    # end new
    "yolo.ezrealeu2+1747983450.755748@outlook.fr": AutoBotInfo(
        playtime_start="08:00", playtime_end="04:00"
    ),
    "enzoodu35@outlook.fr": AutoBotInfo(playtime_start="20:00", playtime_end="08:00"),
    "enzoodu351@outlook.fr": AutoBotInfo(playtime_start="20:00", playtime_end="08:00"),
    "enzoodu352@outlook.fr": AutoBotInfo(playtime_start="20:00", playtime_end="08:00"),
    "enzoooodu35@outlook.fr": AutoBotInfo(playtime_start="20:00", playtime_end="08:00"),
    "enzooodu35@outlook.fr": AutoBotInfo(playtime_start="08:00", playtime_end="20:00"),
    "enzooodu351@outlook.fr": AutoBotInfo(playtime_start="08:00", playtime_end="20:00"),
    "enzooodu352@outlook.fr": AutoBotInfo(playtime_start="08:00", playtime_end="20:00"),
    "enzoooodu351@outlook.fr": AutoBotInfo(
        playtime_start="08:00", playtime_end="20:00"
    ),
}
