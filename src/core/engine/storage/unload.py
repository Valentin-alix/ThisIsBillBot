from dofus_unity_reader.game_constants.npc import BANK_NPCS, NpcInfo

from src.core.config import BOT_KAMA_LIMIT_TO_GIVE
from src.core.engine.movements.map.map_tools import MapTools


def do_unload_on_mule(
    kamas: int,
    is_sub: bool,
) -> bool:
    return kamas > BOT_KAMA_LIMIT_TO_GIVE and is_sub


def get_bank_npc_info(is_sub: bool) -> list[NpcInfo]:
    return [
        npc_info for npc_info in BANK_NPCS if is_sub or MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
    ]
