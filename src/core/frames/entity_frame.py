from dataclasses import dataclass

from db_dofus_unity.protos.game.context_pb2 import ContextRemoveElementEvent
from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    GameRolePlayShowActorsEvent,
)
from src.core.frames.frame import Frame
from src.core.states.entity_state import EntityState
from src.interfaces.enums.priority import PriorityEnum
from src.interfaces.models.entity import Entity


@dataclass
class EntityFrame(Frame):
    entity_state: EntityState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_info_event,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            MapMovementEvent,
            self.on_map_movement_event,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            GameRolePlayShowActorsEvent,
            self.on_game_role_play_show_actors_event,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            ContextRemoveElementEvent,
            self.on_context_remove_element_event,
            priority=PriorityEnum.MAX,
        )

    def on_map_complementary_info_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.entity_state.entities_obstacles.clear()
        self.entity_state.entities_actors_by_id.clear()

        for obstacle in message.obstacles:
            self.entity_state.entities_obstacles.append(
                Entity(cell_id=obstacle.cell_id, entity=obstacle)
            )

        for actor in message.actors:
            self.entity_state.entities_actors_by_id[actor.actor_id] = Entity(
                cell_id=actor.disposition.cell_id, entity=actor
            )

    def on_map_movement_event(self, message: MapMovementEvent):
        related_actor = self.entity_state.entities_actors_by_id[message.character_id]
        if len(message.cells) > 0:
            dst_cell = message.cells[-1]
            related_actor.cell_id = dst_cell
            related_actor.entity.disposition.cell_id = dst_cell
            related_actor.entity.disposition.direction = message.direction

    def on_game_role_play_show_actors_event(self, message: GameRolePlayShowActorsEvent):
        for actor in message.actors:
            self.entity_state.entities_actors_by_id[actor.actor_id] = Entity(
                cell_id=actor.disposition.cell_id, entity=actor
            )

    def on_context_remove_element_event(self, message: ContextRemoveElementEvent):
        self.entity_state.entities_actors_by_id.pop(message.element_id, None)
