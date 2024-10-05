from dataclasses import dataclass, field

from src.core.states.state import State
from db_dofus_unity.protos.game.common_pb2 import ActorPositionInformation
from db_dofus_unity.protos.game.gamemap_pb2 import MapObstacle
from src.interfaces.models.entity import Entity


@dataclass
class EntityState(State):
    entities_actors_by_id: dict[int, Entity[ActorPositionInformation]] = field(
        init=False, default_factory=lambda: {}
    )
    entities_obstacles: list[Entity[MapObstacle]] = field(
        init=False, default_factory=lambda: []
    )

    def get_entity_actor_on_cell_id(
        self, cell_id: int
    ) -> Entity[ActorPositionInformation] | None:
        return next(
            (
                entity
                for entity in self.entities_actors_by_id.values()
                if entity.cell_id == cell_id
            ),
            None,
        )
