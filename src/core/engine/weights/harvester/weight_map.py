from src.const import FAKE_INFINITY_VALUE
from src.core.engine.weights.harvester.weight_collectable import (
    get_map_id_collectable_weight,
)
from src.core.states.game_state import GameState
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB


def get_harvester_additional_weight_by_map_id(
    map_id: int, map_ids_to_explore: set[int], game_state: GameState
):
    if map_id in map_ids_to_explore:
        return FAKE_INFINITY_VALUE
    storage_by_gid = {
        object.item.gid: object
        for objects in CHEST_OBJECT_BY_GID_BY_TAB.values()
        for object in objects.values()
    }
    weight = get_map_id_collectable_weight(
        map_id,
        game_state.player.jobs_lvl_by_id,
        storage_by_gid,
        game_state.player.is_sub,
    )
    return weight
