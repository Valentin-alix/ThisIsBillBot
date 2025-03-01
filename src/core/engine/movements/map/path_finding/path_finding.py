from bisect import insort
from dataclasses import dataclass, field
from time import sleep
from typing import Iterator

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.game_constants.skill import SkillEnum
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint

from src.core.engine.contexts import MapMovementContext
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.map_tools import MapTools
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.node_map_point import NodeMapPoint
from src.core.engine.movements.map.path_finding.path_element import PathElement
from src.core.signals.world_signals import MapSignals
from src.services.logging_utils.loggers import BotLogger

HV_COST: int = 10
DIAG_COST: int = 15
HEURISTIC_SCALE: int = 1

DEBUG_WAIT_TIME: float = 0.01


@dataclass
class Pathfinding:
    data_map_provider: DataMapProvider
    logger: BotLogger
    debug_signals: MapSignals | None = None

    allow_diag: bool = field(init=False, default=True)
    allow_trough_entity: bool = field(init=False, default=True)
    avoid_obstacles: bool = field(init=False, default=True)
    heuristic_scale: int = field(init=False, default=HEURISTIC_SCALE)
    node_by_coord: dict[tuple[int, int], NodeMapPoint] = field(
        init=False, default_factory=dict[tuple[int, int], NodeMapPoint]
    )
    open_list: list[NodeMapPoint] = field(
        init=False, default_factory=list[NodeMapPoint]
    )
    is_coord_closed: set[tuple[int, int]] = field(
        init=False, default_factory=set[tuple[int, int]]
    )
    occupied_cell_ids: set[int] = field(init=False, default_factory=set[int])
    end_columns: set[int] = field(init=False, default_factory=set[int])
    end_lines: set[int] = field(init=False, default_factory=set[int])
    end_x_coords: set[int] = field(init=False, default_factory=set[int])
    end_y_coords: set[int] = field(init=False, default_factory=set[int])

    def get_interactive_near_path(
        self,
        context: MapMovementContext,
        player_mp: MapPoint,
        element_mp: MapPoint,
        skill_ids: list[int],
    ) -> MovementPath | None:
        """get near path for using interactive element"""
        self.data_map_provider.set_context(context)
        minimal_range = 63
        for skill_id in skill_ids:
            skill_data = DataReader().skill_by_id[skill_id]
            if skill_data.range < minimal_range:
                minimal_range = skill_data.range

        near_mps: set[MapPoint] = set()

        if SkillEnum.EXIT in skill_ids:
            near_mps = element_mp.side_map_points
            path_to_element = self.find_path(
                context=context, start=player_mp, ends=near_mps
            )
            if path_to_element.end in near_mps:
                return path_to_element

        if minimal_range > 0:
            for direction in DirectionsEnum:
                mp_direction = self.data_map_provider.get_nearest_free_cell(
                    element_mp, direction
                )
                if mp_direction is not None:
                    near_mps.add(mp_direction)
        if len(near_mps) == 0:
            near_mps = {element_mp}

        path_to_element = self.find_path(
            context=context, start=player_mp, ends=near_mps
        )
        if path_to_element.end.distance_to_map_point(element_mp) - 1 > minimal_range:
            return None

        end_path_mp = (
            path_to_element.path[-1].step
            if len(path_to_element.path) > 0
            else player_mp
        )
        if not self.data_map_provider.can_reach_mp(end_path_mp, element_mp):
            return None

        return path_to_element

    def find_path(
        self,
        context: MapMovementContext,
        start: MapPoint,
        ends: set[MapPoint],
        allow_diag: bool = True,
        allow_trough_entity: bool = True,
        avoid_obstacles: bool = True,
        heuristic_scale: int = HEURISTIC_SCALE,
    ) -> MovementPath:
        self.data_map_provider.set_context(context)
        if self.debug_signals:
            self.debug_signals.white_cell.emit(start)
            self.debug_signals.red_cells.emit(ends)

        self.allow_diag = allow_diag
        self.allow_trough_entity = allow_trough_entity
        self.avoid_obstacles = avoid_obstacles
        self.heuristic_scale = heuristic_scale

        self.open_list.clear()
        self.node_by_coord.clear()
        self.is_coord_closed.clear()

        self.occupied_cell_ids = set(context.occupied_cell_ids)

        self.end_columns = {end.x + end.y for end in ends}
        self.end_lines = {end.x - end.y for end in ends}
        self.end_x_coords = {end.x for end in ends}
        self.end_y_coords = {end.y for end in ends}

        dist_to_end = self.get_heuristic_to_end(start, ends)
        start_node = NodeMapPoint(
            mp=start,
            cost_to_node=0,
            cost_to_end=dist_to_end,
            total_cost=dist_to_end,
            parent=None,
        )

        closest_node: NodeMapPoint = start_node
        insort(self.open_list, start_node)
        start_node.in_open_set = True
        while self.open_list:
            curr_node: NodeMapPoint = self.open_list.pop(0)
            curr_node.in_open_set = False
            if self.debug_signals and curr_node.mp is not start:
                self.debug_signals.green_cell.emit(curr_node.mp)
                sleep(DEBUG_WAIT_TIME)
            if self.is_goal_reached(curr_node, ends):
                return self.build_path(start, curr_node)

            self.is_coord_closed.add((curr_node.mp.x, curr_node.mp.y))
            for node in self.get_neighbors(curr_node.mp):
                cost_to_end: float = self.get_heuristic_to_end(node.mp, ends)
                cost_to_node = (
                    self.get_move_cost(node.mp, curr_node.mp, start, ends, cost_to_end)
                    + curr_node.cost_to_node
                )

                if node.cost_to_node < cost_to_node:
                    continue

                self.node_by_coord[(node.mp.x, node.mp.y)] = node

                if node.in_open_set:
                    self.open_list.remove(node)
                    node.in_open_set = False

                node.cost_to_node = cost_to_node
                node.parent = curr_node
                node.cost_to_end = cost_to_end
                node.total_cost = self.heuristic_scale * cost_to_end + cost_to_node

                if node.cost_to_end < closest_node.cost_to_end:
                    closest_node = node

                insort(self.open_list, node)
                node.in_open_set = True

        mov_path = self.build_path(start, closest_node)
        return mov_path

    def get_heuristic_to_end(self, mp: MapPoint, ends: set[MapPoint]) -> float:
        return min(end.distance_to_map_point(mp) for end in ends)

    def is_goal_reached(self, curr_node: NodeMapPoint, ends: set[MapPoint]) -> bool:
        return curr_node.mp in ends

    def is_cell_on_ends_column(self, map_point: MapPoint) -> bool:
        return (map_point.x + map_point.y) in self.end_columns

    def is_cell_on_ends_line(self, map_point: MapPoint) -> bool:
        return (map_point.x - map_point.y) in self.end_lines

    def get_neighbors(self, parent_mp: MapPoint) -> Iterator[NodeMapPoint]:
        for y in range(parent_mp.y - 1, parent_mp.y + 2):
            for x in range(parent_mp.x - 1, parent_mp.x + 2):
                if (x, y) in self.is_coord_closed or (x, y) not in MAP_POINT_BY_COORD:
                    continue
                node = self.node_by_coord.get((x, y))
                if node:
                    yield node
                    continue
                if (y == parent_mp.y or x == parent_mp.x or self.allow_diag) and (
                    self.is_neighbor((mp := MapPoint.from_coords(x, y)), parent_mp)
                ):
                    yield NodeMapPoint(mp=mp)

    def is_neighbor(self, mp: MapPoint, parent_mp: MapPoint) -> bool:
        can_move_to_parent = self.data_map_provider.can_mov_to_mp(
            mp,
            parent_mp.cell_id,
            allow_through_entity=self.allow_trough_entity,
            avoid_obstacle=self.avoid_obstacles,
        )

        return can_move_to_parent and (
            (parent_mp.x, mp.y) in MAP_POINT_BY_COORD
            and self.data_map_provider.can_mov_to_mp(
                MapPoint.from_coords(parent_mp.x, mp.y),
                parent_mp.cell_id,
                allow_through_entity=self.allow_trough_entity,
                avoid_obstacle=self.avoid_obstacles,
            )
            or (
                (mp.x, parent_mp.y) in MAP_POINT_BY_COORD
                and self.data_map_provider.can_mov_to_mp(
                    MapPoint.from_coords(mp.x, parent_mp.y),
                    parent_mp.cell_id,
                    allow_through_entity=self.allow_trough_entity,
                    avoid_obstacle=self.avoid_obstacles,
                )
            )
        )

    def get_move_cost(
        self,
        mp: MapPoint,
        parent_mp: MapPoint,
        start: MapPoint,
        ends: set[MapPoint],
        cost_to_end: float,
    ) -> float:
        """check cost of move from map point to parent map point"""
        point_weight = self.get_map_point_weight(mp, ends)
        movement_cost: float = (
            DIAG_COST if mp.is_diagonal_move(parent_mp) else HV_COST
        ) * point_weight
        if self.allow_trough_entity:
            is_cell_on_end_column = self.is_cell_on_ends_column(mp)
            is_cell_on_start_column = mp.x + mp.y == start.x + start.y
            is_cell_on_end_line = self.is_cell_on_ends_line(mp)
            is_cell_on_start_line = mp.x - mp.y == start.x - start.y
            if (not is_cell_on_end_column and not is_cell_on_end_line) or (
                not is_cell_on_start_column and not is_cell_on_start_line
            ):
                movement_cost += cost_to_end
                movement_cost += start.distance_to_map_point(mp)

            if mp.x in self.end_x_coords or mp.y in self.end_y_coords:
                movement_cost -= 3

            if (
                is_cell_on_end_column
                or is_cell_on_end_line
                or mp.x + mp.y == parent_mp.x + parent_mp.y
                or mp.x - mp.y == parent_mp.x - parent_mp.y
            ):
                movement_cost -= 2

            if mp.x == start.x or mp.y == start.y:
                movement_cost -= 3

            if is_cell_on_start_column or is_cell_on_start_line:
                movement_cost -= 2

        return movement_cost

    def get_map_point_weight(self, mp: MapPoint, ends: set[MapPoint]) -> float:
        """get weight of map point"""
        if mp in ends:
            return 1

        point_weight: float

        entity_on_cell = mp.cell_id in self.occupied_cell_ids
        if self.allow_trough_entity:
            speed = self.data_map_provider.get_cell_data(mp.cell_id).speed
            if entity_on_cell:
                point_weight = 20
            elif speed >= 0:
                point_weight = 6 - speed
            else:
                point_weight = 12 + abs(speed)
        else:
            point_weight = 1
            if entity_on_cell:
                point_weight += 0.3
            for side_map_point in mp.side_map_points:
                if side_map_point.cell_id in self.occupied_cell_ids:
                    point_weight += 0.3

        return point_weight

    def build_path(self, start: MapPoint, closest_node: NodeMapPoint) -> MovementPath:
        path: list[PathElement] = []

        cursor: NodeMapPoint | None = closest_node

        while cursor and cursor.mp.cell_id != start.cell_id:
            if self.allow_diag:
                # here we check if we can reduce path time by checking parent
                parent = cursor.parent
                grand_parent = parent.parent if parent else None
                grand_grand_parent = grand_parent.parent if grand_parent else None
                if (
                    grand_parent is not None
                    and MapTools.get_distance(
                        cursor.mp.cell_id, grand_parent.mp.cell_id
                    )
                    == 1
                ):
                    if self.data_map_provider.can_mov_to_mp(
                        cursor.mp,
                        grand_parent.mp.cell_id,
                        allow_through_entity=self.allow_trough_entity,
                        avoid_obstacle=self.avoid_obstacles,
                    ):
                        cursor.parent = grand_parent
                elif (
                    grand_grand_parent is not None
                    and MapTools.get_distance(
                        cursor.mp.cell_id, grand_grand_parent.mp.cell_id
                    )
                    == 2
                ):
                    inter_x = cursor.mp.x + round(
                        (grand_grand_parent.mp.x - cursor.mp.x) / 2
                    )
                    inter_y = cursor.mp.y + round(
                        (grand_grand_parent.mp.y - cursor.mp.y) / 2
                    )

                    inter_mp = MapPoint.from_coords(inter_x, inter_y)
                    if (
                        self.data_map_provider.can_mov_to_mp(
                            inter_mp,
                            cursor.mp.cell_id,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                        and self.data_map_provider.get_point_weight(
                            inter_mp, self.allow_trough_entity
                        )
                        < 2
                    ):
                        cursor.parent = self.node_by_coord[(inter_mp.x, inter_mp.y)]
                elif (
                    grand_parent is not None
                    and MapTools.get_distance(
                        cursor.mp.cell_id, grand_parent.mp.cell_id
                    )
                    == 2
                ):
                    assert parent is not None

                    if (
                        cursor.mp.x + cursor.mp.y
                        == grand_parent.mp.x + grand_parent.mp.y
                        and cursor.mp.x - cursor.mp.y != parent.mp.x - parent.mp.y
                        and not self.data_map_provider.is_changing_zone(
                            cursor.mp.cell_id, parent.mp.cell_id
                        )
                        and not self.data_map_provider.is_changing_zone(
                            parent.mp.cell_id, grand_parent.mp.cell_id
                        )
                    ):
                        cursor.parent = grand_parent
                    elif (
                        cursor.mp.x - cursor.mp.y
                        == grand_parent.mp.x - grand_parent.mp.y
                        and cursor.mp.x - cursor.mp.y != parent.mp.x - parent.mp.y
                        and not self.data_map_provider.is_changing_zone(
                            cursor.mp.cell_id, parent.mp.cell_id
                        )
                        and not self.data_map_provider.is_changing_zone(
                            parent.mp.cell_id, grand_parent.mp.cell_id
                        )
                    ):
                        cursor.parent = grand_parent

                    elif (
                        cursor.mp.x == grand_parent.mp.x
                        and cursor.mp.x != parent.mp.x
                        and self.data_map_provider.get_point_weight(
                            MapPoint.from_coords(cursor.mp.x, parent.mp.y),
                            self.allow_trough_entity,
                        )
                        < 2
                        and self.data_map_provider.can_mov_to_mp(
                            MapPoint.from_coords(cursor.mp.x, parent.mp.y),
                            cursor.mp.cell_id,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                    ):
                        cursor.parent = self.node_by_coord[cursor.mp.x, parent.mp.y]

                    elif (
                        cursor.mp.y == grand_parent.mp.y
                        and cursor.mp.y != parent.mp.y
                        and self.data_map_provider.get_point_weight(
                            MapPoint.from_coords(parent.mp.x, cursor.mp.y),
                            self.allow_trough_entity,
                        )
                        < 2
                        and self.data_map_provider.can_mov_to_mp(
                            MapPoint.from_coords(parent.mp.x, cursor.mp.y),
                            cursor.mp.cell_id,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                    ):
                        cursor.parent = self.node_by_coord[parent.mp.x, cursor.mp.y]
            assert cursor.parent is not None
            path.append(
                PathElement(
                    cursor.parent.mp,
                    MapTools.get_look_direction8_exact(
                        cursor.parent.mp.cell_id,
                        cursor.mp.cell_id,
                    ),
                )
            )
            cursor = cursor.parent

        mov_path: MovementPath = MovementPath(start, closest_node.mp, path)
        mov_path.path.reverse()
        return mov_path
