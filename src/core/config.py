import datetime
from random import uniform

from DBDofusUnity.dofus_unity_reader.game_constants.job import JobEnum
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import MapIdEnum


ENABLE_MSG_CAPTURE = False

DEBUG = True

DO_FIGHTER = True
DO_SALE_HOTEL = True
DO_CRAFT = False
DO_USE_GUILD_CHEST = False
DO_DUNGEON = False
DO_QUEST = False

ENABLE_ACCOUNT_AUTOMATION = False
ENABLE_AUTO_EQUIPMENT_MARKET_PURCHASES = False
ENABLE_AUTO_OGRINE_SUBSCRIPTIONS = False
ENABLE_AUTO_PAYSAFECARD_SUBSCRIPTIONS = False

ENABLE_SESSION_CONTEXT = False
DO_IDLE = False


FIGHT_GROUP_LVL_MULTIPLIER = 2
FIGHT_GROUP_LVL_OFFSET = 5


def get_default_fight_group_lvl_limit(level: int) -> float:
    return level * FIGHT_GROUP_LVL_MULTIPLIER + FIGHT_GROUP_LVL_OFFSET


USEFUL_UNLOAD = 0.15

OCCUPIED_MESSAGE_ID: int = 474
OCCUPIED_STUCK_LIMIT = 2

BOT_MINIMAL_KAMAS: int = 2_000_000
MULE_BANK_MAP_ID = MapIdEnum.ASTRUB_BANK

MAX_QUANTITY_ON_SELL = 10_000
MIN_KAMAS_TO_GO_SALE_HOTEL = 1_500

DUNGEON_OFFSET_LVL = 20


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


WEIGHT_BY_JOB: dict[JobEnum, float] = {
    JobEnum.MINER: 5,
    JobEnum.WOODCUTTER: 5,
    JobEnum.ALCHEMIST: 5,
    JobEnum.FISHERMAN: 5,
    JobEnum.PEASANT: 2.5,
    JobEnum.BASE: 1,
}


BETWEEN_COLLECT_PAUSE_PROBABILITY = 0.1
FIRST_COLLECT_MOVEMENT_CANCEL_PROBABILITY = 1 / 3
SUBSEQUENT_COLLECT_MOVEMENT_CANCEL_PROBABILITY = 1 / 8
STATIC_INTERACTION_CANCEL_PROBABILITY = 1 / 8

PLACEMENT_REPOSITIONING_PROBABILITY = 0.08
PLACEMENT_NON_OPTIMAL_MOVE_PROBABILITY = 0.1
