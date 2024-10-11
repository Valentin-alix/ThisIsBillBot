from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from protos.game.gamemap_pb2 import (
    MapChangeRequest,
    MapCurrentEvent,
    MapMovementRefusedEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError


class MapChangeError(StrEnum):
    UNEXPECTED_NEW_MAP = auto()


@dataclass
class MapChangeBehavior(Behavior):
    def run(self, map_id: int, expected_map_id: int):
        self.event_manager.on(
            MapCurrentEvent,
            partial(self.on_map_current_event, expected_map_id=expected_map_id),
            originator=self,
            once=True,
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            self.on_map_movement_refused_event,
            originator=self,
            once=True,
        )
        map_change_request = MapChangeRequest(map_id=map_id)
        self.event_manager.send(map_change_request)

    def on_map_current_event(self, msg: MapCurrentEvent, expected_map_id: int):
        if msg.map_id != expected_map_id:
            return self.finish(MapChangeError.UNEXPECTED_NEW_MAP)
        return self.finish()

    def on_map_movement_refused_event(self, msg: MapMovementRefusedEvent):
        return self.finish(MapMoveError.REFUSED)
