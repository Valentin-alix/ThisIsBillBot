"""
Configuration du comportement du bot (modifiable par l'utilisateur).
Paramètres de stratégie, timings, poids, limites, etc.
"""

import datetime
from random import uniform

from dofus_unity_reader.game_constants.job import JobEnum
from dofus_unity_reader.game_constants.map_id import MapIdEnum

# ============================================================================
# FONCTIONNALITÉS ACTIVÉES
# ============================================================================


DO_FIGHTER = (
    True  # le bot va attacker un groupe de monstre random toutes les 30 minutes
)
DO_SALE_HOTEL = True  # le bot va aller vendre en hdv
DO_CRAFT = False  # le bot va aller craft pr level up principalement
DO_USE_GUILD_CHEST = (
    False  # le bot va utiliser le coffre de guilde plutot que la banque
)
DO_CHAT = False  # le bot va parler en général (avec le model de chatgpt)
DO_REGISTER_PRICE = False  # le bot va faire une requete pour enregistrer le prix a chaque fois qu'on l'obtient
DO_DUNGEON = (
    False  # le bot va aller faire des dongons toutes les 4 heures (si cest possible)
)


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
MULE_BANK_MAP_ID = MapIdEnum.ASTRUB_BANK
MULE_BANK_CHARACTER_LOGIN: set[str] = set()
MULE_BANK_CHARACTER_IDS: set[int] = set()

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
MEDIUM_RANGE = (0.5, 2.5)
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


def get_time_between_attacker() -> datetime.timedelta:
    return (
        datetime.timedelta(minutes=20) * uniform(0.75, 1.25)
        if DO_FIGHTER
        else datetime.timedelta(datetime.MAXYEAR)
    )


def get_time_between_random_chat():
    return (
        datetime.timedelta(hours=45) * uniform(0.75, 1.25)
        if DO_CHAT
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
# HUMANISATION
# ============================================================================

HARVEST_PAUSE_PROBABILITY = 0.05
HARVEST_PAUSE_RANGE = (2.0, 8.0)

AFK_PROBABILITY_PER_MAP = 0.005
AFK_DURATION_RANGE = (30.0, 180.0)

ENABLE_SESSION_CONTEXT = True

PLACEMENT_REPOSITIONING_PROBABILITY = 0.08
PLACEMENT_EXTRA_HESITATION_RANGE = (0.5, 2.0)
PLACEMENT_NON_OPTIMAL_MOVE_PROBABILITY = 0.2

LOOK_AROUND_PROBABILITY = 0.03
LOOK_AROUND_PAUSE_RANGE = (0.3, 1.0)
