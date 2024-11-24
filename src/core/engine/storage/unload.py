from src.core.config import BOT_KAMA_LIMIT_TO_GIVE
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.npcs.npc_info import NpcInfo
from src.core.game_constants import NPCs
from src.core.states.game_state import GameState


def do_unload_on_mule(game_state: GameState):
    return game_state.inventory.kamas > BOT_KAMA_LIMIT_TO_GIVE or (
        not game_state.player.is_sub
        and game_state.sale_hotel.is_full_object_in_sale_hotel
        and not game_state.sale_hotel.should_update_price
    )


def get_bank_npc_info(is_sub: bool) -> list[NpcInfo]:
    return [
        npc_info
        for npc_info in NPCs.BANKS
        if is_sub or MapTools.is_map_allowed_for_unsub(npc_info.npc_map_id)
    ]
