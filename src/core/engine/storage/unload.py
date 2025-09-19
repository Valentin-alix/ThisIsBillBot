from dofus_unity_reader.game_constants.npc import BANK_NPCS, NpcInfo

from src.core.engine.movements.map.map_tools import MapTools


def get_bank_npc_info(is_sub: bool) -> list[NpcInfo]:
    return [
        npc_info for npc_info in BANK_NPCS if is_sub or MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
    ]
