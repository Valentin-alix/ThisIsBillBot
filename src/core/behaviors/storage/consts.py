from src.core.data_center.data_reader import DataReader
from src.interfaces.models.npc_info import NpcInfo

ASTRUB_BANK_MAP = 192415750
BONTA_BANK_MAP = 217059328
BANK_MAP_IDS = [ASTRUB_BANK_MAP, BONTA_BANK_MAP]
ASTRUB_BANK_NPC_INFO = NpcInfo(
    npc_action_id=3, npc_id=-20001, npc_map_id=ASTRUB_BANK_MAP, reply_ids=[64361]
)
BONTA_BANK_NPC_INFO = NpcInfo(
    npc_action_id=3, npc_id=-20000, npc_map_id=BONTA_BANK_MAP, reply_ids=[63535]
)
BANKS_NPC_INFOS = [ASTRUB_BANK_NPC_INFO, BONTA_BANK_NPC_INFO]


PROTECTOR_RACES = [66, 65, 64, 63, 62]
PROTECTOR_DROP_ITEM_IDS = {
    drop.objectId
    for race in PROTECTOR_RACES
    for monster in DataReader().monsters_by_race[race]
    for drop in monster.drops
}
RECIPE_ITEM_IDS: set[int] = {
    17060,
    16499,
    16493,
    16492,
    16491,
    16460,
    16420,
    16419,
    12745,
    7652,
    2543,
    2540,
    748,
}
USEFUL_INGREDIENT_IDS: set[int] = {
    ingredient_id
    for recipe in RECIPE_ITEM_IDS
    for ingredient_id in DataReader().recipe_by_result_id[recipe].ingredientIds
} | {11110, 7033}

GATHERER_ITEM_GIDS: set[int] = {
    harvestable
    for sub_area in DataReader().sub_area_by_id.values()
    for harvestable in sub_area.harvestables
} | {
    311  # water
}

GATHERER_ITEM_TABS = 1


GUILD_CONTENT_BY_TAB = {
    GATHERER_ITEM_TABS: GATHERER_ITEM_GIDS,
    2: PROTECTOR_DROP_ITEM_IDS | RECIPE_ITEM_IDS,
}


USEFUL_UNLOAD = 0.15
