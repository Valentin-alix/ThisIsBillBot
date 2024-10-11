from src.core.logic.grid.map_point import MapPoint
from src.core.states.entity_state import ActorByMpDict


def is_entity_actor_on_cell_id(actor_on_mp: ActorByMpDict, cell_id: int) -> bool:
    actors_on_mp = actor_on_mp.get(MapPoint.from_cell_id(cell_id))
    return actors_on_mp is not None and len(actors_on_mp) > 0
