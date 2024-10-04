from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
)
from src.core.handlers.handler import Handler
from src.core.states.map_state import MapState


@dataclass
class MapHandler(Handler):
    map_state: MapState

    def __post_init__(self):
        self.msg_event.received_game_msg.connect(
            self.on_map_complementary_information_event,
            MapComplementaryInformationEvent,
        )
        self.msg_event.received_game_msg.connect(
            self.on_map_movement_event, MapMovementEvent
        )

    def on_map_complementary_information_event(
        self, _, message: MapComplementaryInformationEvent
    ):
        self.map_state.map = message

    def on_map_movement_event(self, _, message: MapMovementEvent):
        for actor in self.map_state.map.actors:
            if not actor.actor_id == message.character_id:
                continue
            actor.disposition.cell_id = message.cells[-1]
            actor.disposition.direction = message.direction
