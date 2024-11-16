from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapChangeRequest,
    MapCurrentEvent,
    MapMovementRefusedEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.events_manager.priority import PriorityEnum


class MapChangeError(StrEnum):
    UNEXPECTED_NEW_MAP = auto()
    TIMEOUT = auto()


@dataclass
class MapChangeBehavior(Behavior):
    def run(self, map_id: int, expected_map_id: int):
        self.event_manager.on(
            MapCurrentEvent,
            partial(self.on_map_current_event, expected_map_id=expected_map_id),
            originator=self,
            once=True,
            timeout=30,
            on_timeout=lambda: self.finish(MapChangeError.TIMEOUT),
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            self.on_map_movement_refused_event,
            originator=self,
            once=True,
            priority=PriorityEnum.MAX,
        )
        map_change_request = MapChangeRequest(map_id=map_id)
        self.event_manager.send(map_change_request)

    def on_map_current_event(self, msg: MapCurrentEvent, expected_map_id: int):
        if msg.map_id != expected_map_id:
            return self.finish(MapChangeError.UNEXPECTED_NEW_MAP)
        return self.finish()

    def on_map_movement_refused_event(self, msg: MapMovementRefusedEvent):
        if (
            MapPoint.from_coords(msg.cell_x, msg.cell_y)
            != self.game_state.map.map_point
        ):
            return self.finish(MapMoveError.INVALID_STARTING_POINT)
        return self.finish(MapMoveError.REFUSED)
