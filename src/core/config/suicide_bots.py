import random
from src.core.behaviors.storage.consts import ASTRUB_BANK_MAP

MULE_KAMAS_MAP_ID = ASTRUB_BANK_MAP
MULE_BANK_CHARACTER_ID: int | None = 22466789726
# 21089026398
BOT_MINIMAL_KAMAS: int = 500_000
BOT_KAMA_LIMIT_TO_GIVE: int = 800_000

NOT_SUICIDE_BOT_LOGINS: list[str] = [
    "ezrealeu44700_main@outlook.com",
    "ezrealeu44700_1+s4@outlook.com",
    "ezrealeu44700_2+s7@outlook.com",
    "ezrealeu44700_2+s8@outlook.com",
]
INCARNAM_BOT_LOGINS = random.sample(
    NOT_SUICIDE_BOT_LOGINS, len(NOT_SUICIDE_BOT_LOGINS) // 3
)
SUICIDE_BOT_FIGHT_LEVEL_LIMIT = 15
