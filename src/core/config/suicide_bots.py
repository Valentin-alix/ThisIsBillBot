from pydantic import BaseModel

from src.core.behaviors.storage.consts import ASTRUB_BANK_MAP
from src.interfaces.enums.area_enum import AreaEnum, SubAreaEnum

MULE_KAMAS_MAP_ID = ASTRUB_BANK_MAP
MULE_BANK_CHARACTER_ID: int | None = 22466789726
MULE_BANK_CHARACTER_LOGIN: str | None = None

BOT_MINIMAL_KAMAS: int = 1_000_000
BOT_KAMA_LIMIT_TO_GIVE: int = 1_500_000


HARVESTABLE_AREAS_UNSUB_WITH_WEIGHT: list[tuple[dict[str, int | None], float, int]] = [
    ({"area_id": AreaEnum.INCARNAM, "sub_area_id": None}, 1, 1),
    ({"area_id": AreaEnum.ASTRUB, "sub_area_id": None}, 3, 10),
]
FIGHTABLE_AREAS_UNSUB_WITH_WEIGHT: list[tuple[dict[str, int | None], float, int]] = [
    ({"area_id": AreaEnum.ASTRUB, "sub_area_id": SubAreaEnum.ASTRUB_CITY}, 3, 15),
    ({"area_id": AreaEnum.ASTRUB, "sub_area_id": SubAreaEnum.ASTRUB_MEADOW}, 6, 25),
    ({"area_id": AreaEnum.ASTRUB, "sub_area_id": SubAreaEnum.ASTRUB_SEWERS}, 6, 25),
    (
        {"area_id": AreaEnum.INCARNAM, "sub_area_id": SubAreaEnum.INCARNAM_SOUL_ROAD},
        1,
        1,
    ),
    ({"area_id": AreaEnum.INCARNAM, "sub_area_id": SubAreaEnum.INCARNAM_FIELD}, 1, 5),
    ({"area_id": AreaEnum.INCARNAM, "sub_area_id": SubAreaEnum.INCARNAM_FOREST}, 1, 5),
]
HARVESTABLE_AREAS_SUB_WITH_WEIGHT = HARVESTABLE_AREAS_UNSUB_WITH_WEIGHT
FIGHTABLE_AREAS_SUB_WITH_WEIGHT = FIGHTABLE_AREAS_UNSUB_WITH_WEIGHT


HARVESTER_WEIGHT_ACTION = 1.5
FIGHTER_WEIGHT_ACTION = 1


class SuicideBotInfo(BaseModel):
    playtime_start: str
    playtime_end: str


SUICIDE_BOT_INFOS: dict[str, SuicideBotInfo] = {
    "yolo.ezrealeu0+1746797145.3525991@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu0+1746797206.5805416@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu0+1746797286.9255104@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu0+1746797363.2857757@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu1+1746910861.8072877@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu1+1746910940.6129506@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu1+1746911015.9603567@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu1+1746911095.7343402@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu1+1746991985.9399312@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1746992063.2369444@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1746992220.7215219@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1747073760.6615245@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    # First PC
    "yolo.ezrealeu1+1747383728.8980427@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1747383803.7312455@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1747383881.9948237@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    "yolo.ezrealeu1+1747383961.6163003@outlook.fr": SuicideBotInfo(
        playtime_start="04:00", playtime_end="12:00"
    ),
    # new
    # "yolo.ezrealeu2+1747935351.2405686@outlook.fr": SuicideBotInfo(
    #     playtime_start="04:00", playtime_end="12:00"
    # ),
    # "yolo.ezrealeu2+1747935431.2478561@outlook.fr": SuicideBotInfo(
    #     playtime_start="04:00", playtime_end="12:00"
    # ),
    # end new
    "yolo.ezrealeu2+1747486192.297596@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu2+1747486269.6553888@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu2+1747486344.6269078@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    "yolo.ezrealeu2+1747486424.979286@outlook.fr": SuicideBotInfo(
        playtime_start="12:00", playtime_end="20:00"
    ),
    # new
    # "yolo.ezrealeu2+1747935509.5774288@outlook.fr": SuicideBotInfo(
    #     playtime_start="12:00", playtime_end="20:00"
    # ),
    # "yolo.ezrealeu2+1747935591.7806125@outlook.fr": SuicideBotInfo(
    #     playtime_start="12:00", playtime_end="20:00"
    # ),
    # end new
    "yolo.ezrealeu2+1747580509.2676435@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu2+1747580588.7733128@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu2+1747580666.3935292@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    "yolo.ezrealeu2+1747580751.6996515@outlook.fr": SuicideBotInfo(
        playtime_start="20:00", playtime_end="04:00"
    ),
    # new
    # "yolo.ezrealeu2+1747983370.305707@outlook.fr": SuicideBotInfo(
    #     playtime_start="20:00", playtime_end="04:00"
    # ),
    # "yolo.ezrealeu2+1747983450.755748@outlook.fr": SuicideBotInfo(
    #     playtime_start="20:00", playtime_end="04:00"
    # ),
    # end new
}
