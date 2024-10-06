from dataclasses import dataclass

from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    FightMapInformationEvent,
)
from src.core.frames.frame import Frame
from src.core.states.map_state import MapState


@dataclass
class MapFrame(Frame):
    map_state: MapState

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
        )

        self.event_manager.on(
            FightMapInformationEvent,
            callback=self.on_fight_map_information_event,
            originator=self,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.map_state.map_id = message.map_id
        self.map_state.subarea_id = message.subarea_id

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.map_state.map_id = msg.map_id
