from dataclasses import dataclass, field

from db_dofus_unity.protos.game.common_pb2 import (
    ActorPositionInformation,
)
from db_dofus_unity.protos.game.gamemap_pb2 import MapObstacle
from src.core.states.state import State


@dataclass
class EntityState(State):
    actor_by_id: dict[int, ActorPositionInformation] = field(
        init=False, default_factory=dict
    )
    map_obstacle_by_cell_id: dict[int, MapObstacle] = field(
        init=False, default_factory=dict
    )

    def is_entity_actor_on_cell_id(self, cell_id: int) -> bool:
        for actor in self.actor_by_id.values():
            if actor.disposition.cell_id == cell_id:
                return True
        return False
