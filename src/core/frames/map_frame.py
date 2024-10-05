from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from src.core.frames.frame import Frame
from src.core.states.entity_state import EntityState
from src.core.states.map_state import MapState
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class MapFrame(Frame):
    entity_state: EntityState
    map_state: MapState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            priority=PriorityEnum.MAX,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.map_state.map_id = message.map_id
        self.map_state.subarea_id = message.subarea_id
