"""
Configuration du comportement du bot (modifiable par l'utilisateur).
Paramètres de stratégie, timings, poids, limites, etc.

✅ Ces valeurs PEUVENT et DOIVENT être ajustées selon vos besoins.
Elles définissent comment votre bot se comporte, pas le jeu lui-même.

Pour les constantes du jeu, voir src/core/game_constants.py
"""

import datetime
from random import uniform

from D3Database.enums.area_enum import AreaEnum, SubAreaEnum
from D3Database.enums.jobs_enum import JobEnum
from src.core.engine.movements.area_infos import AreaInfo
from src.core.game_constants import Maps

# ============================================================================
# FONCTIONNALITÉS ACTIVÉES
# ============================================================================

DO_EXTRA_ACTION = True
DO_FIGHTER = True
DO_SALE_HOTEL = True
DO_CRAFT = True
DO_DUNGEON = False
DO_USE_GUILD_CHEST = True
DO_REGISTER_PRICE = False


# ============================================================================
# LIMITES & SEUILS
# ============================================================================

# Farming
LVL_LIMIT_FOR_HARVEST = 10
KAMAS_LIMIT_FOR_HARVEST = 5_000

# Storage
USEFUL_UNLOAD = 0.15

# Mule
BOT_MINIMAL_KAMAS: int = 2_000_000
BOT_KAMA_LIMIT_TO_GIVE: int = 8_000_000
MULE_BANK_MAP_ID = Maps.ASTRUB_BANK
MULE_BANK_CHARACTER_LOGIN: set[str] = set()

# Sale Hotel
MAX_QUANTITY_ON_SELL = 10_000
MIN_KAMAS_TO_GO_SALE_HOTEL = 1_500

# Dungeon
DUNGEON_OFFSET_LVL = 20


# ============================================================================
# TIMINGS (en secondes, tuples = ranges)
# ============================================================================

# Waiting times timing
VERY_SMALL_RANGE = (0.2, 0.4)
TINY_RANGE = (0.2, 0.8)
SMALL_RANGE = (0.3, 1)
BASE_RANGE = (0.5, 1.5)
BIG_RANGE = (1, 3)
ON_NEW_MAP_BEFORE_ACTION = (0.5, 4.5)

# Bank
ON_OPENED_INVENTORY = BASE_RANGE
BEFORE_CLOSING_INVENTORY = BASE_RANGE

# Npc
BETWEEN_REPLY = BASE_RANGE

# Scraping
INTERVAL_BETWEEN_SCRAPING = 60 * 14


# ============================================================================
# TIMINGS DYNAMIQUES (fonctions)
# ============================================================================


def get_time_beween_sale_hotel_prices():
    return datetime.timedelta(hours=4, minutes=0) * uniform(0.75, 1.25)


def get_time_beween_areas():
    return datetime.timedelta(hours=1) * uniform(0.75, 1.25)


def get_time_between_attacker():
    return (
        datetime.timedelta(minutes=20) * uniform(0.75, 1.25)
        if DO_FIGHTER
        else datetime.timedelta(datetime.MAXYEAR)
    )


def get_time_between_random_chat():
    return (
        datetime.timedelta(hours=45) * uniform(0.75, 1.25)
        if DO_EXTRA_ACTION
        else datetime.timedelta(datetime.MAXYEAR)
    )


def get_time_between_dungeon():
    return (
        datetime.timedelta(hours=4) * uniform(0.75, 1.25)
        if DO_DUNGEON
        else datetime.timedelta(datetime.MAXYEAR)
    )


# ============================================================================
# POIDS & PRIORITÉS
# ============================================================================

WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 5,
    JobEnum.WOODCUTTER: 5,
    JobEnum.ALCHEMIST: 5,
    JobEnum.FISHERMAN: 5,
    JobEnum.PEASANT: 2.5,
    JobEnum.BASE: 1,
}


# ============================================================================
# ZONES DE FARMING
# ============================================================================

AREAS_UNSUB_WITH_WEIGHT: list[AreaInfo] = [
    AreaInfo(area_id=AreaEnum.INCARNAM),
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
    AreaInfo(area_id=AreaEnum.FRIGOST, min_lvl=91, waypoint_id_needed=54172969),
    AreaInfo(area_id=AreaEnum.PANDALA, min_lvl=91, waypoint_id_needed=207619076),
    AreaInfo(
        area_id=AreaEnum.OTOMAI,
        min_lvl=111,
        waypoint_id_needed=207619076,
    ),
]
