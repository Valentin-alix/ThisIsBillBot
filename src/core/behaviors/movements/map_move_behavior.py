from dataclasses import dataclass
from enum import StrEnum, auto
from functools import partial

from db_dofus_unity.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceType,
)
from db_dofus_unity.protos.game.gamemap_pb2 import (
    MapMovementRequest,
    MapMovementConfirmRequest,
    MapMovementEvent,
)
from src.common.logger import Logger
from src.core.behaviors.behavior import Behavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.fight_state import FightState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState


class MapMoveError(StrEnum):
    INVALID_PATH = auto()


@dataclass
class MapMoveBehavior(Behavior):
    fight_state: FightState
    player_state: PlayerState
    inventory_state: InventoryState
    map_state: MapState
    path_finding: Pathfinding

    def run(self, move_path: MovementPath):
        Logger().info(f"Going to : {move_path.end}")
        if self.player_state.map_point != move_path.start:
            Logger().error(
                f"Invalid starting point : {move_path.end}, player map point is {self.player_state.map_point}"
            )
            return self.finish(MapMoveError.INVALID_PATH)

        if self.player_state.map_point.cell_id == move_path.end.cell_id:
            return self.finish()

        key_cells = move_path.get_key_cells()
        if self.fight_state.in_fight:
            self.event_manager.on(
                SequenceEndEvent,
                self.on_sequence_end_event,
                originator=self,
            )
        else:
            self.event_manager.on(
                MapMovementEvent,
                callback=partial(
                    self.on_map_movement_event,
                    duration=move_path.get_total_duration(
                        False,
                        self.inventory_state.inventory_weight,
                        self.inventory_state.weight_max,
                    ),
                    move_path=move_path,
                ),
                originator=self,
            )

        map_movement_request = MapMovementRequest(
            key_cells=key_cells, map_id=self.map_state.map_id
        )
        self.event_manager.send(map_movement_request)

    def on_map_movement_event(
        self, msg: MapMovementEvent, duration: float, move_path: MovementPath
    ):
        if self.player_state.character_id == msg.character_id:
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

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.sequence_type == SequenceType.MOVE
            and msg.author_id == self.player_state.character_id
        ):
            self.event_manager.on(
                GameActionAcknowledgementRequest,
                partial(
                    self.on_game_action_acknowledgement_request,
                    target_action_id=msg.action_id,
                ),
                originator=self,
            )

    def on_game_action_acknowledgement_request(
        self, msg: GameActionAcknowledgementRequest, target_action_id: int
    ):
        if msg.action_id == target_action_id:
            self.finish()

    def get_move_path_to_cell_id(self, cell_id: int) -> MovementPath | None:
        if self.player_state.map_point.cell_id == cell_id:
            return None
        end_map_point = MapPoint.from_cell_id(cell_id)
        movement_path = self.path_finding.find_path(
            self.player_state.map_point,
            {end_map_point},
            allow_diag=not self.fight_state.in_fight,
            allow_trough_entity=not self.fight_state.in_fight,
        )
        return movement_path
