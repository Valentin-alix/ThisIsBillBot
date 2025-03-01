from dataclasses import dataclass, field

from datas.protos.non_obf.game.gamemap_pb2 import MapObstacle
from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.consts import MAP_COUNT_CELL, MAP_WIDTH
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.engine.contexts import MapMovementContext

TOLERANCE_ELEVATION: int = 11


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
        """check if mps are on same level"""
        context = self._get_context()
        from_mp_data = MapReader().get_cell_data_by_cell_id(
            context.map_id, from_mp.cell_id
        )
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
        mov = bool(cell_data.mov) and not (
            context.in_fight and cell_data.nonWalkableDuringFight
        )
        if not mov:
            return False

        if previous_cell_id is not None and previous_cell_id != map_point.cell_id:
            if not self.can_reach_mp(
                MapPoint.from_cell_id(previous_cell_id), map_point
            ):
                return False

        if avoid_obstacle:
            related_obstacle = context.obstacle_on_cell_id.get(map_point.cell_id)
            if (
                related_obstacle
                and not related_obstacle.state == MapObstacle.OBSTACLE_OPENED
            ):
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
                if MapPoint.from_coords(coord_x, coord_y).cell_id in (
                    context.occupied_cell_ids
                ):
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

    def get_nearest_free_cell(
        self,
        map_point: MapPoint,
        orientation: DirectionsEnum,
        allow_itself: bool = True,
        allow_though_entity: bool = True,
        ignore_speed: bool = False,
        forbidden_mps: set[MapPoint] | None = None,
    ) -> MapPoint | None:
        if forbidden_mps is None:
            forbidden_mps = set()

        min_weight_mp: tuple[MapPoint, int] | None = None
        for curr_orientation in DirectionsEnum:
            near_mp = map_point.get_nearest_mp_in_direction(curr_orientation)
            if near_mp is None:
                continue

            curr_orientation_dist = DirectionsEnum.get_distance(
                curr_orientation, orientation
            )
            speed: int = self.get_cell_data(near_mp.cell_id).speed
            mp_can_move = self.can_mov_to_mp(
                near_mp,
                map_point.cell_id,
                allow_through_entity=allow_though_entity,
            )
            if not mp_can_move:
                forbidden_mps.add(near_mp)
                continue

            curr_weight_orientation = curr_orientation_dist + (
                (5 - speed if speed >= 0 else 11 + abs(speed))
                if not ignore_speed
                else 0
            )
            if near_mp in forbidden_mps:
                curr_weight_orientation += 100

            if min_weight_mp is None or curr_weight_orientation < min_weight_mp[1]:
                min_weight_mp = (near_mp, curr_weight_orientation)

        if (
            min_weight_mp is None
            and allow_itself
            and self.can_mov_to_mp(
                map_point,
                map_point.cell_id,
                allow_through_entity=allow_though_entity,
            )
        ):
            return map_point
        return min_weight_mp[0] if min_weight_mp is not None else None

    def does_allows_map_change_to_direction(
        self, mp: MapPoint, direction: DirectionsEnum
    ) -> bool:
        cell_data = self.get_cell_data(mp.cell_id)
        match direction:
            case DirectionsEnum.RIGHT:
                return (
                    bool(cell_data.mapChangeData & 1)
                    or (
                        (mp.cell_id + 1) % (MAP_WIDTH * 2) == 0
                        and bool(cell_data.mapChangeData & 2)
                    )
                    or (
                        (mp.cell_id + 1) % (MAP_WIDTH * 2) == 0
                        and bool(cell_data.mapChangeData & 128)
                    )
                )
            case DirectionsEnum.LEFT:
                return (
                    (mp.x == -mp.y and bool(cell_data.mapChangeData & 8))
                    or bool(cell_data.mapChangeData & 16)
                    or (mp.x == -mp.y and bool(cell_data.mapChangeData & 32))
                )
            case DirectionsEnum.UP:
                return (
                    (mp.cell_id < MAP_WIDTH and bool(cell_data.mapChangeData & 32))
                    or bool(cell_data.mapChangeData & 64)
                    or (mp.cell_id < MAP_WIDTH and bool(cell_data.mapChangeData & 128))
                )
            case DirectionsEnum.DOWN:
                return (
                    (
                        mp.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                        and bool(cell_data.mapChangeData & 2)
                    )
                    or bool(cell_data.mapChangeData & 4)
                    or (
                        mp.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                        and bool(cell_data.mapChangeData & 8)
                    )
                )
            case _:
                return False

    def allows_map_change_to_direction(self, mp: MapPoint, direction: DirectionsEnum):
        map_change_data = self.get_cell_data(mp.cell_id).mapChangeData
        if direction == DirectionsEnum.RIGHT:
            return (
                bool(map_change_data & 1)
                or (
                    (mp.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 2)
                )
                or (
                    (mp.cell_id + 1) % (MAP_WIDTH * 2) == 0
                    and bool(map_change_data & 128)
                )
            )
        elif direction == DirectionsEnum.LEFT:
            return (
                (mp.x == -mp.y and bool(map_change_data & 8))
                or bool(map_change_data & 16)
                or (mp.x == -mp.y and bool(map_change_data & 32))
            )
        elif direction == DirectionsEnum.UP:
            return (
                (mp.cell_id < MAP_WIDTH and bool(map_change_data & 32))
                or bool(map_change_data & 64)
                or (mp.cell_id < MAP_WIDTH and bool(map_change_data & 128))
            )
        elif direction == DirectionsEnum.DOWN:
            return (
                (mp.cell_id >= MAP_COUNT_CELL - MAP_WIDTH and bool(map_change_data & 2))
                or bool(map_change_data & 4)
                or (
                    mp.cell_id >= MAP_COUNT_CELL - MAP_WIDTH
                    and bool(map_change_data & 8)
                )
            )

        return False
