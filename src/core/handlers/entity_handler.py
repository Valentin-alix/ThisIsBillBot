from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.context_pb2 import ContextRemoveElementEvent
from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
    GameRolePlayShowActorsEvent,
)
from src.core.handlers.handler import Handler
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.states.entity_state import EntityState, Entity
from src.core.states.player_state import PlayerState


@dataclass
class EntityHandler(Handler):
    entity_state: EntityState
    player_state: PlayerState
    data_map_provider: DataMapProvider

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(
            self.on_map_complementary_info_event, MapComplementaryInformationEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_map_movement_event, MapMovementEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_game_role_play_show_actors_event, GameRolePlayShowActorsEvent
        )
        self.msg_event.received_game_msg.connect(
            self.on_context_remove_element_event, ContextRemoveElementEvent
        )

    def on_map_complementary_info_event(
        self, _, message: MapComplementaryInformationEvent
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

    def on_map_movement_event(self, _, message: MapMovementEvent):
        dst_cell = message.cells[-1]
        if message.character_id in self.entity_state.entities_actors_by_id:
            self.entity_state.entities_actors_by_id[message.character_id].cell_id = (
                dst_cell
            )

    def on_game_role_play_show_actors_event(
        self, _, message: GameRolePlayShowActorsEvent
    ):
        for actor in message.actors:
            self.entity_state.entities_actors_by_id[actor.actor_id] = Entity(
                cell_id=actor.disposition.cell_id, entity=actor
            )

    def on_context_remove_element_event(self, _, message: ContextRemoveElementEvent):
        self.entity_state.entities_actors_by_id.pop(message.element_id, None)
