from dataclasses import dataclass

from protos.game.character_pb2 import CharacterLifeStatusEvent
from protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    FightMapInformationEvent,
    MapCurrentEvent,
)
from src.core.data_center.data_reader import DataReader
from src.core.frames.frame import Frame
from src.signals.world_signals import WorldSignals


@dataclass
class MapFrame(Frame):
    world_signals: WorldSignals

    def __post_init__(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            self.on_map_complementary_information_event,
            originator=self,
        )

        self.event_manager.on(
            MapCurrentEvent, self.on_map_current_event, originator=self
        )

        self.event_manager.on(
            FightMapInformationEvent,
            callback=self.on_fight_map_information_event,
            originator=self,
        )
        self.event_manager.on(
            CharacterLifeStatusEvent,
            self.on_character_life_status_event,
            originator=self,
        )

    def on_map_complementary_information_event(
        self, message: MapComplementaryInformationEvent
    ):
        self.logger.info(f"New map : {message.map_id}")
        self.game_state.map.map_id = message.map_id
        self.world_signals.curr_map_pos.emit(
            DataReader().map_pos_by_map_id[message.map_id]
        )

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.map.map_id = msg.map_id

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.game_state.map.map_id = msg.map_id

    def on_character_life_status_event(self, msg: CharacterLifeStatusEvent):
        self.game_state.map.phoenix_map_id = msg.phoenix_map_id
