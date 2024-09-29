from typing import List


from src.core.logic.path_finding.consts import INFINITE_COST, MAP_COUNT_CELL
from src.core.logic.path_finding.data_map_provider import DataMapProvider
from src.core.logic.path_finding.map_point import MapPoint
from src.core.logic.path_finding.map_tools import MapTools


class Pathfinding:
    _is_init: bool = False
    _parent_of_cell: List[int]
    _open_list_weights: List[int]
    _is_cell_closed: List[bool]
    _is_entity_on_cell: List[bool]
    _open_list: list

    @staticmethod
    def find_path(
        start: MapPoint,
        end: MapPoint,
        allow_diag: bool = True,
        allow_through_entity: bool = True,
        avoid_obstacles: bool = True,
    ):
        cost_of_cell: dict[int, int] = {}
        open_list_weights: dict[int, int] = {}
        parent_of_cell: dict[int, int | None] = {}
        is_cell_closed: dict[int, bool] = {}
        is_entity_on_cell: dict[int, bool] = {}
        open_list: list[int] = []

        start_cell_id = start.cell_id
        end_cell_id = end.cell_id

        for i in range(MAP_COUNT_CELL):
            parent_of_cell[i] = None
            is_cell_closed[i] = False
            is_entity_on_cell[i] = False

        DataMapProvider.fill_entity_on_cell_array(
            is_entity_on_cell, allow_through_entity
        )
        cost_of_cell[start_cell_id] = 0

        open_list.append(start_cell_id)
        while len(open_list) > 0 and not is_cell_closed[end_cell_id]:
            minimum = INFINITE_COST
            smallest_cost_index = 0

            for i in range(len(open_list)):
                cost = open_list_weights[open_list[i]]
                if cost <= minimum:
                    minimum = cost
                    smallest_cost_index = i

            parent_id = open_list[smallest_cost_index]
            parent_x = MapTools.get_cell_x_by_id(parent_id)
            parent_y = MapTools.get_cell_y_by_id(parent_id)
            open_list.remove(smallest_cost_index)
            is_cell_closed[parent_id]

            # if(cellId != MapTools.INVALID_CELL_ID && _isCellClosed[cellId] == false && cellId != parentId && map.pointMov(x,y,bAllowTroughEntity,parentId,endCellId,avoidObstacles) && (y == parentY || x == parentX || allowDiag && (map.pointMov(parentX,y,bAllowTroughEntity,parentId,endCellId,avoidObstacles) || map.pointMov(x,parentY,bAllowTroughEntity,parentId,endCellId,avoidObstacles))))
            for y in range(parent_y - 1, parent_y + 1):
                for x in range(parent_x - 1, parent_x + 1):
                    cell_id = MapTools.get_cell_id_by_coord(x, y)
                    if (
                        not is_cell_closed[cell_id]
                        and cell_id != parent_id
                        and DataMapProvider.point_mov(
                            x,
                            y,
                            allow_through_entity,
                            parent_id,
                            end_cell_id,
                            avoid_obstacles,
                        )
                        and (
                            y == parent_x
                            or x == parent_x
                            or allow_diag
                            and (
                                DataMapProvider.point_mov(
                                    parent_x,
                                    y,
                                    allow_through_entity,
                                    parent_id,
                                    end_cell_id,
                                    avoid_obstacles,
                                )
                                or DataMapProvider.point_mov(
                                    x,
                                    parent_y,
                                    allow_through_entity,
                                    parent_id,
                                    end_cell_id,
                                    avoid_obstacles,
                                )
                            )
                        )
                    ):
                        point_weight = 0
                        if cell_id == end_cell_id:
                            point_weight = 1
                        else:
                            speed = 1  # TODO Get speed from cell data
                            if allow_through_entity:
                                if is_entity_on_cell[cell_id]:
                                    point_weight = 20
                                elif speed >= 0:
                                    point_weight = 6 - speed
                                else:
                                    point_weight = 12 + abs(speed)
                            else:
                                point_weight = 1
                                if is_entity_on_cell[cell_id]:
                                    point_weight += 0.3
                                if (
                                    MapTools.is_valid_coord(x + 1, y)
                                    and is_entity_on_cell[
                                        MapTools.get_cell_id_by_coord(x + 1, y)
                                    ]
                                ):
                                    point_weight += 0.3
                                if (
                                    MapTools.is_valid_coord(x, y + 1)
                                    and is_entity_on_cell[
                                        MapTools.get_cell_id_by_coord(x, y + 1)
                                    ]
                                ):
                                    point_weight += 0.3
                                if (
                                    MapTools.is_valid_coord(x - 1, y)
                                    and is_entity_on_cell[
                                        MapTools.get_cell_id_by_coord(x - 1, y)
                                    ]
                                ):
                                    point_weight += 0.3
                                if (
                                    MapTools.is_valid_coord(x, y - 1)
                                    and is_entity_on_cell[
                                        MapTools.get_cell_id_by_coord(x, y - 1)
                                    ]
                                ):
                                    point_weight += 0.3
                                if (
                                    DataMapProvider.point_special_effects(x, y) & 2
                                ) == 2:
                                    point_weight += 0.2
