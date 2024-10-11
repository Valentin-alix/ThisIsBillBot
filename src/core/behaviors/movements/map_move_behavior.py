from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceType,
)
from protos.game.gamemap_pb2 import (
    MapMovementRequest,
    MapMovementConfirmRequest,
    MapMovementEvent,
    MapMovementRefusedEvent,
)
from src.core.behaviors.behavior import Behavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding


class MapMoveError(StrEnum):
    CANCELED_MOVEMENT = auto()
    REFUSED = auto()


@dataclass
class MapMoveBehavior(Behavior):
    path_finding: Pathfinding

    def run(self, move_path: MovementPath):
        self.logger.info(f"Going to : {move_path.end}")
        if self.game_state.player.map_point != move_path.start:
            raise ValueError(
                f"Invalid starting point : {move_path.end}, player map point is {self.game_state.player.map_point}"
            )

        if self.game_state.player.map_point.cell_id == move_path.end.cell_id:
            return self.finish()

        key_cells = move_path.get_key_cells()
        if self.game_state.fight.in_fight:
            self.event_manager.on(
                SequenceEndEvent,
                partial(self.on_sequence_end_event, end_mp=move_path.end),
                originator=self,
            )
        else:
            self.event_manager.on(
                MapMovementEvent,
                callback=partial(
                    self.on_map_movement_event,
                    duration=move_path.get_total_duration(
                        self.game_state.player.is_riding,
                        self.game_state.inventory.inventory_weight,
                        self.game_state.inventory.weight_max,
                    ),
                    move_path=move_path,
                ),
                originator=self,
            )

        self.event_manager.on(
            MapMovementRefusedEvent, self.on_map_movement_refused_event, originator=self
        )
        map_movement_request = MapMovementRequest(
            key_cells=key_cells, map_id=self.game_state.map.map_id
        )
        self.event_manager.send(map_movement_request)

    def on_sequence_end_event(self, msg: SequenceEndEvent, end_mp: MapPoint):
        if (
            msg.sequence_type == SequenceType.MOVE
            and msg.author_id == self.game_state.player.character_id
        ):
            self.event_manager.clear_listener_by_origin_and_type(SequenceEndEvent, self)
            self.event_manager.on(
                GameActionAcknowledgementRequest,
                partial(
                    self.on_game_action_acknowledgement_request,
                    target_action_id=msg.action_id,
                    end_mp=end_mp,
                ),
                originator=self,
            )

    def on_game_action_acknowledgement_request(
        self,
        msg: GameActionAcknowledgementRequest,
        target_action_id: int,
        end_mp: MapPoint,
    ):
        if msg.action_id == target_action_id:
            if self.game_state.player.map_point != end_mp:
                self.logger.info(f"Movement was canceled.")
                return self.finish(MapMoveError.CANCELED_MOVEMENT)
            self.finish()

    def on_map_movement_event(
        self, msg: MapMovementEvent, duration: float, move_path: MovementPath
    ):
        if self.game_state.player.character_id == msg.character_id:
            if move_path.end.cell_id != msg.cells[-1]:
                return self.finish(MapMoveError.CANCELED_MOVEMENT)
            self.event_manager.on(
                MapMovementConfirmRequest,
                callback=lambda _: self.finish(),
                originator=self,
                once=True,
                timeout=duration,
                on_timeout=self.send_map_movement_confirm,
            )

    def send_map_movement_confirm(self):
        req = MapMovementConfirmRequest()
        self.event_manager.send(req)

    def on_map_movement_refused_event(self, msg: MapMovementRefusedEvent):
        return self.finish(MapMoveError.REFUSED)
