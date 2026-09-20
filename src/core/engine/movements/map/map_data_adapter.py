from dataclasses import dataclass, field

from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import MapObstacle
from DBDofusUnity.dofus_unity_reader.data_center.map_reader import MapReader
from DBDofusUnity.dofus_unity_reader.game_constants.directions import DirectionsEnum
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.contexts import MapMovementContext

TOLERANCE_ELEVATION: int = 11
BLOCKED_CELL_SPEED: int = -100
FORBIDDEN_CELL_WEIGHT: int = 1000


@dataclass
class DataMapProvider:
    context: MapMovementContext | None = field(init=False, default=None)

    def set_context(self, context: MapMovementContext) -> None:
        self.context = context

    def _get_context(self) -> MapMovementContext:
        if self.context is None:
            raise RuntimeError("Map movement context must be set before pathing")
        return self.context

    @property
    def map_data(self):
        return MapReader().map_by_id(self._get_context().map_id)

    def get_cell_data(self, cell_id: int):
        return self.map_data.mapData.cellsData[cell_id]

    def can_reach_mp(self, from_mp: MapPoint, to_mp: MapPoint) -> bool:
        context = self._get_context()
        from_mp_data = MapReader().get_cell_data_by_cell_id(context.map_id, from_mp.cell_id)
        to_mp_data = MapReader().get_cell_data_by_cell_id(context.map_id, to_mp.cell_id)
        dif_floor = abs(from_mp_data.floor - to_mp_data.floor)

        if MapReader().is_map_using_new_movement_system(context.map_id) and (
            (to_mp_data.moveZone != from_mp_data.moveZone and dif_floor > 0)
            or (
                to_mp_data.moveZone == from_mp_data.moveZone
                and from_mp_data.moveZone == 0
                and dif_floor > TOLERANCE_ELEVATION
            )
        ):
            return False
        return True

    def can_mov_to_mp(
        self,
        map_point: MapPoint,
        previous_cell_id: int | None = None,
        allow_through_entity: bool = True,
        avoid_obstacle: bool = True,
    ):
        context = self._get_context()
        cell_data = self.get_cell_data(map_point.cell_id)
        mov = bool(cell_data.mov) and not (context.in_fight and cell_data.nonWalkableDuringFight)
        if not mov:
            return False

        if previous_cell_id is not None and previous_cell_id != map_point.cell_id:
            if not self.can_reach_mp(MapPoint.from_cell_id(previous_cell_id), map_point):
                return False

        if avoid_obstacle:
            related_obstacle = context.obstacle_on_cell_id.get(map_point.cell_id)
            if related_obstacle and not related_obstacle.state == MapObstacle.OBSTACLE_OPENED:
                return False

        if not allow_through_entity:
            if map_point.cell_id in context.occupied_cell_ids:
                return False

        return True

    def get_point_weight(
        self,
        mp: MapPoint,
        allow_trough_entity: bool = True,
    ) -> float:
        weight: float = 1
        speed: int = self.get_cell_data(mp.cell_id).speed
        if allow_trough_entity:
            if speed >= 0:
                weight += 5 - speed
            else:
                weight += 11 + abs(speed)

        else:
            context = self._get_context()
            if mp.cell_id in context.occupied_cell_ids:
                weight += 0.3

            coords: list[tuple[int, int]] = [
                (mp.x + 1, mp.y),
                (mp.x, mp.y + 1),
                (mp.x - 1, mp.y),
                (mp.x, mp.y - 1),
            ]
            for coord_x, coord_y in coords:
                if MapPoint.from_coords(coord_x, coord_y).cell_id in (context.occupied_cell_ids):
                    weight += 0.3

        return weight

    def is_changing_zone(self, cell_id_1: int, cell_id_2: int) -> bool:
        cell_1_data = self.get_cell_data(cell_id_1)
        cell_2_data = self.get_cell_data(cell_id_2)
        dif: int = abs(abs(cell_1_data.floor) - abs(cell_2_data.floor))
        return cell_1_data.moveZone != cell_2_data.moveZone and dif == 0

    def is_changing_map(self, cell_id: int) -> bool:
        cell_1_data = self.get_cell_data(cell_id)
        return cell_1_data.mapChangeData != 0

    def is_farm_cell(self, cell_id: int) -> bool:
        return bool(self.get_cell_data(cell_id).farmCell)

    def get_nearest_free_cell(
        self,
        map_point: MapPoint,
        orientation: DirectionsEnum,
        allow_itself: bool = True,
        allow_though_entity: bool = True,
        ignore_speed: bool = False,
        forbidden_cell_ids: frozenset[int] = frozenset(),
    ) -> MapPoint | None:
        """Blocked neighbours remain candidates with a speed penalty, so the result may be non-walkable."""
        candidates: list[MapPoint | None] = []
        weights: list[int] = []

        for curr_orientation in DirectionsEnum:
            near_mp = map_point.get_nearest_mp_in_direction(curr_orientation)
            if near_mp is None or near_mp.cell_id in forbidden_cell_ids:
                candidates.append(near_mp)
                weights.append(FORBIDDEN_CELL_WEIGHT)
                continue

            speed: int = self.get_cell_data(near_mp.cell_id).speed
            if not self.can_mov_to_mp(near_mp, map_point.cell_id, allow_through_entity=allow_though_entity):
                speed = BLOCKED_CELL_SPEED

            candidates.append(near_mp)
            weights.append(
                DirectionsEnum.get_distance(curr_orientation, orientation)
                + (0 if ignore_speed else (5 - speed if speed >= 0 else 11 + abs(speed)))
            )

        best_index = 0
        for index in range(1, len(weights)):
            if weights[index] < weights[best_index] and candidates[index] is not None:
                best_index = index

        best_mp = candidates[best_index]
        if (
            best_mp is None
            and allow_itself
            and self.can_mov_to_mp(map_point, map_point.cell_id, allow_through_entity=allow_though_entity)
        ):
            return map_point
        return best_mp
