import random
from dataclasses import dataclass
from functools import partial

from datas.protos.non_obf.game.gamemap_pb2 import (
    MapMovementCancelRequest,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapMovementRequest,
)
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_CELL_ID

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding

DECOY_MIN_DISTANCE = 5
DECOY_MAX_DISTANCE = 10
CANCEL_FRACTION_RANGE = (0.3, 0.7)
DECOY_MOVEMENT_TIMEOUT = 3.0
CANCEL_LATENCY_MARGIN = 0.15
CANCEL_SETTLE_RANGE = (0.2, 0.45)


@dataclass
class MapMovementCancelBehavior(Behavior):
    path_finding: Pathfinding
    map_move_behavior: MapMoveBehavior

    def run(self, final_move_path: MovementPath):
        current_mp = self.game_state.map.map_point
        context = self.game_state.get_map_movement_context()

        candidates = [
            mp
            for mp in MAP_POINT_BY_CELL_ID.values()
            if DECOY_MIN_DISTANCE <= current_mp.distance_to_map_point(mp) <= DECOY_MAX_DISTANCE
        ]
        random.shuffle(candidates)

        decoy_path: MovementPath | None = None
        for candidate in candidates:
            path = self.path_finding.find_path(context, current_mp, {candidate})
            if path.end.cell_id == candidate.cell_id and len(path.path) >= 2:
                decoy_path = path
                break

        if decoy_path is None:
            self.logger.info("No decoy cell found, moving directly to final destination")
            return self._start_final_move(final_move_path)

        self.logger.info(f"Human-like move: decoy to {decoy_path.end}, then to {final_move_path.end}")
        self.event_manager.on(
            MapMovementEvent,
            partial(self.on_decoy_movement_event, final_move_path=final_move_path),
            originator=self,
            timeout=DECOY_MOVEMENT_TIMEOUT,
            on_timeout=lambda: self._start_final_move(final_move_path),
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            lambda _: self._start_final_move(final_move_path),
            originator=self,
            once=True,
        )

        self.event_manager.send(
            MapMovementRequest(key_cells=decoy_path.get_key_cells(), map_id=self.game_state.map.map_id)
        )

    def on_decoy_movement_event(self, msg: MapMovementEvent, final_move_path: MovementPath):
        if msg.character_id != self.game_state.player.character_id:
            return
        self.unregister_listener(MapMovementEvent, reason="Decoy movement confirmed, scheduling cancel")
        self.unregister_listener(MapMovementRefusedEvent, reason="Decoy movement confirmed")

        cells = list(msg.cells)
        path_elements = MovementPath.get_path_elements_from_cells(cells)

        last_cancellable_index = len(cells) - 2
        if last_cancellable_index < 1:
            return self._do_cancel(cells[-1], final_move_path)

        fraction = random.uniform(*CANCEL_FRACTION_RANGE)
        cancel_index = max(1, min(last_cancellable_index, round((len(cells) - 1) * fraction)))
        cancel_cell_id = cells[cancel_index]

        duration = MovementPath.get_duration_until(
            path_elements,
            cancel_index,
            self.game_state.inventory.inventory_weight,
            self.game_state.inventory.weight_max,
        )
        duration = max(0.0, duration - CANCEL_LATENCY_MARGIN)
        self.run_timer(duration, partial(self._do_cancel, cancel_cell_id, final_move_path))

    def _do_cancel(self, cancel_cell_id: int, final_move_path: MovementPath):
        self.logger.info(f"Cancelling decoy movement at cell {cancel_cell_id}")
        self.event_manager.send(MapMovementCancelRequest(cell_id=cancel_cell_id))
        self.run_timer(CANCEL_SETTLE_RANGE, partial(self._start_final_move_from_current, final_move_path))

    def _start_final_move_from_current(self, final_move_path: MovementPath):
        final_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(), self.game_state.map.map_point, {final_move_path.end}
        )
        self._start_final_move(final_path)

    def _start_final_move(self, move_path: MovementPath):
        self.map_move_behavior.start(callback=self.finish, parent=self, move_path=move_path)
