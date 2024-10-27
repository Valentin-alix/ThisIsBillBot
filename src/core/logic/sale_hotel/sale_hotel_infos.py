from enums.category_item_enum import CategoryEnum
from src.interfaces.models.npc_info import NpcInfo


BONTA_SALE_HOTEL_RES_SELL_ACTION = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=212601350
)

BONTA_SALE_HOTEL_COM_SELL_ACTION = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=212600839
)

ASTRUB_SALE_HOTEL_RES_SELL_ACTION = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=191104004
)
ASTRUB_SALE_HOTEL_COM_SELL_ACTION = NpcInfo(
    npc_id=-1, npc_action_id=5, npc_map_id=191102976
)

SALE_HOTELS_BY_CATEGORY: dict[CategoryEnum, list[NpcInfo]] = {
    CategoryEnum.RESOURCES: [
        BONTA_SALE_HOTEL_RES_SELL_ACTION,
        ASTRUB_SALE_HOTEL_RES_SELL_ACTION,
    ],
    CategoryEnum.CONSUMABLES: [
        BONTA_SALE_HOTEL_COM_SELL_ACTION,
        ASTRUB_SALE_HOTEL_COM_SELL_ACTION,
    ],
}


UNSUB_SALE_HOTEL = [
    ASTRUB_SALE_HOTEL_COM_SELL_ACTION,
    ASTRUB_SALE_HOTEL_RES_SELL_ACTION,
]
SUB_SALE_HOTEL = [BONTA_SALE_HOTEL_RES_SELL_ACTION]
