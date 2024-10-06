from dataclasses import dataclass

from db_dofus_unity.protos.game.context_pb2 import (
    ContextRemoveElementEvent,
)
from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    GameRolePlayShowActorsEvent,
)
from src.core.frames.frame import Frame
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState


@dataclass
class EntityFrame(Frame):
    entity_state: EntityState
    fight_state: FightState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_info_event,
            originator=self,
        )
        self.event_manager.on(
            MapMovementEvent,
            self.on_map_movement_event,
            originator=self,
        )
        self.event_manager.on(
            GameRolePlayShowActorsEvent,
            self.on_game_role_play_show_actors_event,
            originator=self,
        )
        self.event_manager.on(
            ContextRemoveElementEvent,
            self.on_context_remove_element_event,
            originator=self,
        )

    def on_map_complementary_info_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.entity_state.map_obstacle_by_cell_id = {
            obstacle.cell_id: obstacle for obstacle in message.obstacles
        }
        self.entity_state.actor_by_id = {
            actor.actor_id: actor for actor in message.actors
        }

    def on_map_movement_event(self, message: MapMovementEvent):
        if self.fight_state.in_fight:
            return
        if message.character_id not in self.entity_state.actor_by_id:
            return
        related_actor = self.entity_state.actor_by_id[message.character_id]
        if len(message.cells) > 0:
            related_actor.disposition.cell_id = message.cells[-1]
        related_actor.disposition.direction = message.direction

    def on_game_role_play_show_actors_event(self, message: GameRolePlayShowActorsEvent):
        for actor in message.actors:
            self.entity_state.actor_by_id[actor.actor_id] = actor

    def on_context_remove_element_event(self, message: ContextRemoveElementEvent):
        if (
            self.fight_state.in_fight
            and message.element_id in self.entity_state.actor_by_id
        ):
            self.entity_state.actor_by_id.pop(message.element_id)
