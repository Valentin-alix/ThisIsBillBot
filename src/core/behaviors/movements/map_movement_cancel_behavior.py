import random
from dataclasses import dataclass, field
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import (
    MapCurrentEvent,
    MapMovementCancelRequest,
    MapMovementEvent,
    MapMovementRefusedEvent,
    MapMovementRequest,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior, MapMoveError
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.events_manager.priority import PriorityEnum

CANCELLED_PATH_REMAINING_CELLS_RANGE = (1, 3)
FAKE_DESTINATION_LATERAL_OFFSET_RANGE = (1, 4)
FAKE_DESTINATION_PATH_PROGRESS = (0.30, 0.5, 0.75)
MOVEMENT_TIMEOUT = 3.0
CANCEL_LATENCY_MARGIN = 0.15
CANCEL_SETTLE_RANGE = (0.2, 0.45)


@dataclass
class MapMovementCancelBehavior(Behavior):
    path_finding: Pathfinding
    map_move_behavior: MapMoveBehavior

    _watch_actor_id: int | None = field(init=False, default=None)

    def run(
        self,
        final_move_path: MovementPath,
        cancellation_probability: float,
        watch_actor_id: int | None = None,
    ) -> None:
        assert 0 <= cancellation_probability <= 1, "Cancellation probability must be between zero and one"
        self._watch_actor_id = watch_actor_id
        if random.random() >= cancellation_probability:
            self._start_final_move(final_move_path)
            return

        self.event_manager.on(
            MapCurrentEvent,
            lambda _: self.finish(MapMoveError.UNEXPECTED_NEW_MAP),
            originator=self,
            once=True,
            priority=PriorityEnum.MAX,
        )

        if len(final_move_path.path) < 2:
            return self._start_final_move(final_move_path)

        fake_move_path = self._find_fake_move_path(final_move_path)
        if fake_move_path is None:
            self.logger.info("No fake destination near final path, moving directly to final destination")
            return self._start_final_move(final_move_path)

        self.logger.info(
            f"Human-like move: fake destination {fake_move_path.end}, then {final_move_path.end}"
        )
        self.event_manager.on(
            MapMovementEvent,
            partial(self.on_movement_event, final_move_path=final_move_path),
            originator=self,
            timeout=MOVEMENT_TIMEOUT,
            on_timeout=lambda: self._start_final_move(final_move_path),
        )
        self.event_manager.on(
            MapMovementRefusedEvent,
            lambda _: self._start_final_move(final_move_path),
            originator=self,
            once=True,
        )

        self.event_manager.send(
            MapMovementRequest(key_cells=fake_move_path.get_key_cells(), map_id=self.game_state.map.map_id)
        )

    def _find_fake_move_path(self, final_move_path: MovementPath) -> MovementPath | None:
        current_map_point = self.game_state.map.map_point
        context = self.game_state.get_map_movement_context()
        final_path_cell_ids = {path_element.step.cell_id for path_element in final_move_path.path}
        fake_destinations = self._get_lateral_fake_destinations(
            current_map_point,
            final_move_path.end,
            final_path_cell_ids,
        )
        random.shuffle(fake_destinations)
        for fake_destination in fake_destinations:
            fake_move_path = self.path_finding.find_path(context, current_map_point, {fake_destination})
            if self._is_usable_fake_move_path(fake_move_path, fake_destination, final_move_path.end):
                return fake_move_path
        return None

    @staticmethod
    def _get_lateral_fake_destinations(
        start_map_point: MapPoint,
        final_map_point: MapPoint,
        final_path_cell_ids: set[int],
    ) -> list[MapPoint]:
        path_delta_x = final_map_point.x - start_map_point.x
        path_delta_y = final_map_point.y - start_map_point.y
        path_length = max(abs(path_delta_x), abs(path_delta_y))
        if path_length == 0:
            return []

        lateral_unit_x = -path_delta_y / path_length
        lateral_unit_y = path_delta_x / path_length
        fake_destinations: list[MapPoint] = []
        for path_progress in FAKE_DESTINATION_PATH_PROGRESS:
            for lateral_offset in range(
                FAKE_DESTINATION_LATERAL_OFFSET_RANGE[0], FAKE_DESTINATION_LATERAL_OFFSET_RANGE[1] + 1
            ):
                for side in (-1, 1):
                    candidate_coordinate = (
                        round(
                            start_map_point.x
                            + path_delta_x * path_progress
                            + lateral_unit_x * lateral_offset * side
                        ),
                        round(
                            start_map_point.y
                            + path_delta_y * path_progress
                            + lateral_unit_y * lateral_offset * side
                        ),
                    )
                    if candidate_coordinate not in MAP_POINT_BY_COORD:
                        continue
                    candidate = MapPoint.from_coords(*candidate_coordinate)
                    if (
                        MapMovementCancelBehavior._is_between_start_and_end(
                            candidate, start_map_point, final_map_point
                        )
                        and candidate.cell_id not in final_path_cell_ids
                    ):
                        fake_destinations.append(candidate)
        return fake_destinations

    @staticmethod
    def _is_between_start_and_end(
        candidate: MapPoint,
        start_map_point: MapPoint,
        final_map_point: MapPoint,
    ) -> bool:
        path_delta_x = final_map_point.x - start_map_point.x
        path_delta_y = final_map_point.y - start_map_point.y
        candidate_delta_x = candidate.x - start_map_point.x
        candidate_delta_y = candidate.y - start_map_point.y
        path_projection = candidate_delta_x * path_delta_x + candidate_delta_y * path_delta_y
        path_length_squared = path_delta_x**2 + path_delta_y**2
        return 0 < path_projection < path_length_squared

    @staticmethod
    def _is_usable_fake_move_path(
        fake_move_path: MovementPath,
        fake_destination: MapPoint,
        final_map_point: MapPoint,
    ) -> bool:
        fake_path_cell_ids = {path_element.step.cell_id for path_element in fake_move_path.path}
        return (
            fake_move_path.end.cell_id == fake_destination.cell_id
            and final_map_point.cell_id not in fake_path_cell_ids
            and len(fake_move_path.path) >= 2
        )

    def on_movement_event(self, msg: MapMovementEvent, final_move_path: MovementPath) -> None:
        if msg.character_id != self.game_state.player.character_id:
            return
        self.unregister_listener(MapMovementEvent, reason="Movement confirmed, scheduling cancel")
        self.unregister_listener(MapMovementRefusedEvent, reason="Movement confirmed")

        cells = list(msg.cells)
        path_elements = MovementPath.get_path_elements_from_cells(cells)

        last_cancellable_index = len(cells) - 2
        if last_cancellable_index < 1:
            return self._do_cancel(cells[-1], final_move_path)

        remaining_cells = random.randint(
            CANCELLED_PATH_REMAINING_CELLS_RANGE[0],
            min(CANCELLED_PATH_REMAINING_CELLS_RANGE[1], last_cancellable_index),
        )
        cancel_index = len(cells) - 1 - remaining_cells
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
        self.logger.info(f"Cancelling fake movement at cell {cancel_cell_id}")
        self.event_manager.send(MapMovementCancelRequest(cell_id=cancel_cell_id))
        self.run_timer(CANCEL_SETTLE_RANGE, partial(self._start_final_move_from_current, final_move_path))

    def _start_final_move_from_current(self, final_move_path: MovementPath):
        final_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(), self.game_state.map.map_point, {final_move_path.end}
        )
        self._start_final_move(final_path)

    def _start_final_move(self, move_path: MovementPath):
        self.map_move_behavior.start(
            callback=self.finish, parent=self, move_path=move_path, watch_actor_id=self._watch_actor_id
        )
