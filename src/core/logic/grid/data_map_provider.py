from dataclasses import dataclass

from com.ankama.dofus.server.game.protocol.gamemap_pb2 import MapObstacle
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.map_tools import MapTools
from src.core.repositories.map_reader import MapReader
from src.core.states.entity_state import EntityState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState

TOLERANCE_ELEVATION: int = 11


@dataclass
class DataMapProvider:
    entity_state: EntityState
    player_state: PlayerState
    map_state: MapState

    def get_cell_data(self, cell_id: int):
        cell_data = (
            MapReader().map_by_id(self.map_state.map.map_id).cellsData.Array[cell_id]
        )
        return cell_data

    def fill_entity_on_cell_array(
        self,
        cell_array: dict[int, bool],
        allow_through_entity: bool,
    ):
        if not allow_through_entity:
            for cell_id, actor in self.entity_state.entities_actors_by_id.items():
                cell_array[cell_id] = True

    def can_mov(
        self,
        x: int,
        y: int,
        allow_through_entity: bool = True,
        previous_cell_id: int = -1,
        end_cell_id: int = -1,
        avoid_obstacle: bool = True,
    ):
        if not MapPoint.is_in_map(x, y):
            return False

        data_map = MapReader().map_by_id(self.map_state.map.map_id)
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        cell_data = data_map.cellsData.Array[cell_id]

        mov = bool(cell_data.mov) and (
            not self.player_state.is_in_fight or not cell_data.nonWalkableDuringFight
        )
        if mov and previous_cell_id != -1 and previous_cell_id != cell_id:
            previous_cell_data = data_map.cellsData.Array[previous_cell_id]
            dif = abs(abs(cell_data.floor - abs(previous_cell_data.floor)))
            if (
                previous_cell_data.moveZone != cell_data.moveZone
                and dif > 0
                or previous_cell_data.moveZone == cell_data.moveZone
                and cell_data.moveZone == 0
                and dif > TOLERANCE_ELEVATION
            ):
                mov = False
        if not allow_through_entity and cell_id != end_cell_id:
            for entity_obstacle in self.entity_state.entities_obstacles:
                if entity_obstacle.cell_id == cell_id and (
                    entity_obstacle.entity.state == MapObstacle.OBSTACLE_CLOSED
                    or avoid_obstacle
                ):
                    return False

        return mov

    def get_point_weight(
        self,
        x: int,
        y: int,
        allow_trough_entity: bool = True,
    ) -> float:
        weight: float = 1
        cell_id: int = MapTools.get_cell_id_by_coord(x, y)
        speed: int = self.get_cell_data(cell_id).speed
        if allow_trough_entity:
            if speed >= 0:
                weight += 5 - speed
            else:
                weight += 11 + abs(speed)

            if self.entity_state.get_entity_actor_on_cell_id(cell_id) is not None:
                weight = 20
        else:
            if self.entity_state.get_entity_actor_on_cell_id(cell_id) is not None:
                weight += 0.3

            if self.entity_state.get_entity_actor_on_cell_id(
                MapTools.get_cell_id_by_coord(x + 1, y)
            ):
                weight += 0.3

            if self.entity_state.get_entity_actor_on_cell_id(
                MapTools.get_cell_id_by_coord(x, y + 1)
            ):
                weight += 0.3

            if self.entity_state.get_entity_actor_on_cell_id(
                MapTools.get_cell_id_by_coord(x - 1, y)
            ):
                weight += 0.3

            if self.entity_state.get_entity_actor_on_cell_id(
                MapTools.get_cell_id_by_coord(x, y - 1)
            ):
                weight += 0.3

        return weight

    def is_change_zone(self, cell1: int, cell2: int) -> bool:
        cell_1_data = self.get_cell_data(cell1)
        cell_2_data = self.get_cell_data(cell2)
        dif: int = abs(abs(cell_1_data.floor) - abs(cell_2_data.floor))
        return cell_1_data.moveZone != cell_2_data.moveZone and dif == 0

    def is_change_map(self, cell_id: int) -> bool:
        cell_1_data = self.get_cell_data(cell_id)
        return cell_1_data.mapChangeData != 0

    def get_nearest_free_cell_in_direction(
        self,
        map_point: MapPoint,
        orientation: int,
        allow_itself: bool = True,
        allow_though_entity: bool = True,
        ignore_speed: bool = False,
        forbidden_cells_id: list[int] | None = None,
    ) -> MapPoint | None:
        if forbidden_cells_id is None:
            forbidden_cells_id = []
        cells: list[MapPoint | None] = 8 * [None]
        weights: list[int] = list[int](8 * [-1])
        orientation_dist = [
            MapPoint.get_orientations_distance(i, orientation) for i in range(8)
        ]
        for curr_orientation in range(8):
            mp = map_point.get_nearest_mp_in_direction(curr_orientation)
            cells[curr_orientation] = mp
            if mp is None:
                weights[curr_orientation] = -1
                continue
            speed: int = self.get_cell_data(mp.cell_id).speed
            if mp.cell_id not in forbidden_cells_id:
                if self.can_mov(
                    mp.point.x, mp.point.y, allow_though_entity, map_point.cell_id
                ):
                    weights[curr_orientation] = orientation_dist[curr_orientation] + (
                        (5 - speed if speed >= 0 else 11 + abs(speed))
                        if not ignore_speed
                        else 0
                    )
                else:
                    forbidden_cells_id.append(mp.cell_id)
                    weights[curr_orientation] = -1
            else:
                if self.can_mov(
                    mp.point.x, mp.point.y, allow_though_entity, map_point.cell_id
                ):
                    weights[curr_orientation] = (
                        100
                        + orientation_dist[curr_orientation]
                        + (
                            (5 - speed if speed >= 0 else 11 + abs(speed))
                            if not ignore_speed
                            else 0
                        )
                    )
                else:
                    weights[curr_orientation] = -1

        min_weight_orientation: int = -1
        min_weight: int = 10000
        for curr_orientation in range(8):
            if (
                weights[curr_orientation] != -1
                and weights[curr_orientation] < min_weight
                and cells[curr_orientation] is not None
            ):
                min_weight = weights[curr_orientation]
                min_weight_orientation = curr_orientation
        if min_weight_orientation != -1:
            mp = cells[min_weight_orientation]
        else:
            mp = None
        if (
            mp is None
            and allow_itself
            and self.can_mov(
                map_point.point.x,
                map_point.point.y,
                allow_though_entity,
                map_point.cell_id,
            )
        ):
            return map_point
        return mp
