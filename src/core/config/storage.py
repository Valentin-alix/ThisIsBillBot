from enums.item_enum import ItemEnum
from enums.type_item_enum import TypeItemEnum

from D3Database.data_center.data_reader import DataReader
from src.interfaces.models.npc_info import NpcInfo

ASTRUB_BANK_MAP = 192415750
BONTA_BANK_MAP = 217059328
BANK_MAP_IDS = [ASTRUB_BANK_MAP, BONTA_BANK_MAP]
ASTRUB_BANK_NPC_INFO = NpcInfo(
    npc_id=-20001, npc_map_id=ASTRUB_BANK_MAP, include_reply_ids=[64361]
)
BONTA_BANK_NPC_INFO = NpcInfo(
    npc_id=-20000, npc_map_id=BONTA_BANK_MAP, include_reply_ids=[63535]
)
BANKS_NPC_INFOS = [ASTRUB_BANK_NPC_INFO, BONTA_BANK_NPC_INFO]


PROTECTOR_RACES = [66, 65, 64, 63, 62]
PROTECTOR_DROP_ITEM_IDS = {
    drop.objectId
    for race in PROTECTOR_RACES
    for monster in DataReader().monsters_by_race[race]
    for drop in monster.drops
    if DataReader().item_by_id[drop.objectId].typeId
    not in [310, TypeItemEnum.PIERRE_BRUTE]
}

CUSTOM_GATHERER_ITEM_BY_SAC_GID = {7989: 1794, 7993: 1784, 11112: 11107}


GATHERER_ITEM_GIDS: set[int] = {
    harvestable
    for sub_area in DataReader().sub_area_by_id.values()
    for harvestable in sub_area.harvestables
    if harvestable in DataReader().item_by_id
} | {ItemEnum.WATER}

SELLABLE_ITEMS = (
    GATHERER_ITEM_GIDS
    | DataReader().item_ids_by_type_id[TypeItemEnum.SUBSTRAT]
    | DataReader().item_ids_by_type_id[TypeItemEnum.ALLIAGE]
)

GIDS_BY_TAB = {
    1: GATHERER_ITEM_GIDS,
    2: DataReader().item_ids_by_type_id[TypeItemEnum.PLANCHE]
    | DataReader().item_ids_by_type_id[TypeItemEnum.PREPARATION]
    | DataReader().item_ids_by_type_id[TypeItemEnum.SUBSTRAT]
    | DataReader().item_ids_by_type_id[TypeItemEnum.ALLIAGE]
    | PROTECTOR_DROP_ITEM_IDS,
}
TAB_BY_GID = {gid: tab for tab, gids in GIDS_BY_TAB.items() for gid in gids}


USEFUL_UNLOAD = 0.15
