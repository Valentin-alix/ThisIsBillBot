import sys
from dataclasses import dataclass, field
from threading import Thread
from time import sleep
from typing import Iterator

import icecream
from PyQt5.QtWidgets import QApplication
from sortedcontainers import SortedSet

from src.common.debugger import timeit
from src.common.logger import Logger
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint, MAP_POINT_BY_COORD
from src.core.logic.grid.map_tools import MapTools
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.node_map_point import NodeMapPoint
from src.core.logic.grid.path_finding.path_element import PathElement
from src.core.repositories.data_reader import DataReader
from src.core.repositories.map_reader import MapReader
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.interactive_state import InteractiveState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.gui.components.grid_widget import GridView
from src.signals.grid_signals import GridSignals
from src.signals.path_finding_signals import PathFindingSignals
from src.signals.player_signals import GameInfoSignals

HV_COST: int = 10
DIAG_COST: int = 15
HEURISTIC_SCALE: int = 1

DEBUG_WAIT_TIME: float = 0.01


@dataclass
class Pathfinding:
    data_map_provider: DataMapProvider
    player_state: PlayerState
    map_state: MapState
    entity_state: EntityState

    path_finding_signals: PathFindingSignals | None = None
    allow_diag: bool = field(init=False, default=True)
    allow_trough_entity: bool = field(init=False, default=True)
    avoid_obstacles: bool = field(init=False, default=True)
    heuristic_scale: int = field(init=False, default=HEURISTIC_SCALE)

    node_by_coord: dict[tuple[int, int], NodeMapPoint] = field(
        init=False, default_factory=dict
    )
    open_list: SortedSet[NodeMapPoint] = field(init=False, default_factory=SortedSet)
    is_coord_closed: set[tuple[int, int]] = field(init=False, default_factory=set)

    def find_path_to_interactive(
        self, element_id: int, skill_id: int
    ) -> MovementPath | None:
        skill_range = DataReader().skill_by_id[skill_id].range
        cell_id_element = (
            MapReader()
            .get_ref_data_by_element_id(self.map_state.map_id)[element_id]
            .cellId
        )

        mp_element = MapPoint.from_cell_id(cell_id_element)
        ends = {mp_element}
        ends |= {map_point for end in ends for map_point in end.side_map_points}

        move_path = self.find_path(self.player_state.map_point, ends)
        if move_path.end.distance_to_map_point(mp_element) > skill_range:
            return None

        return move_path

    @timeit
    def find_path(
        self,
        start: MapPoint,
        ends: set[MapPoint],
        allow_diag: bool = True,
        allow_trough_entity: bool = True,
        avoid_obstacles: bool = True,
        heuristic_scale: int = HEURISTIC_SCALE,
    ) -> MovementPath:
        Logger().info(
            f"finding path from {start} to :{ends} at map {self.map_state.map_id}"
        )
        if self.path_finding_signals:
            self.path_finding_signals.start_cell.emit(start)
            self.path_finding_signals.end_cells.emit(ends)
        self.allow_diag = allow_diag
        self.allow_trough_entity = allow_trough_entity
        self.avoid_obstacles = avoid_obstacles
        self.heuristic_scale = heuristic_scale

        self.open_list.clear()
        self.node_by_coord.clear()
        self.is_coord_closed.clear()

        dist_to_end = self.get_heuristic_to_end(start, ends)
        start_node = NodeMapPoint(
            mp=start,
            cost_to_node=0,
            cost_to_end=dist_to_end,
            total_cost=dist_to_end,
            parent=None,
        )

        closest_node: NodeMapPoint = start_node
        self.open_list.add(start_node)
        start_node.in_open_set = True
        while self.open_list:
            curr_node = self.open_list.pop(0)
            curr_node.in_open_set = False
            if self.path_finding_signals and curr_node.mp is not start:
                self.path_finding_signals.treated_cell.emit(curr_node.mp)
                sleep(DEBUG_WAIT_TIME)
            if self.is_goal_reached(curr_node, ends):
                return self.build_path(start, curr_node)
            self.is_coord_closed.add((curr_node.mp.x, curr_node.mp.y))
            for node in self.get_neighbors(curr_node.mp, ends):
                cost_to_node = (
                    self.get_move_cost(node.mp, curr_node.mp, start, ends)
                    + curr_node.cost_to_node
                )

                if node.cost_to_node < cost_to_node:
                    continue

                self.node_by_coord[(node.mp.x, node.mp.y)] = node

                if node.in_open_set:
                    self.open_list.remove(node)
                    node.in_open_set = False

                cost_to_end: float = self.get_heuristic_to_end(node.mp, ends)
                node.cost_to_node = cost_to_node
                node.parent = curr_node
                node.cost_to_end = cost_to_end
                node.total_cost = self.heuristic_scale * cost_to_end + cost_to_node

                if node.cost_to_end < closest_node.cost_to_end:
                    closest_node = node

                self.open_list.add(node)
                node.in_open_set = True

        mov_path = self.build_path(start, closest_node)
        return mov_path

    def get_heuristic_to_end(self, mp: MapPoint, ends: set[MapPoint]) -> float:
        return min(end.distance_to_map_point(mp) for end in ends)

    def is_goal_reached(self, curr_node: NodeMapPoint, ends: set[MapPoint]):
        return curr_node.mp in ends

    def is_cell_on_ends_column(self, map_point: MapPoint, ends: set[MapPoint]) -> bool:
        return any(map_point.x + map_point.y == end.x + end.y for end in ends)

    def is_cell_on_ends_line(self, map_point: MapPoint, ends: set[MapPoint]) -> bool:
        return any(map_point.x - map_point.y == end.x - end.y for end in ends)

    def get_neighbors(
        self, parent_mp: MapPoint, ends: set[MapPoint]
    ) -> Iterator[NodeMapPoint]:
        for y in range(parent_mp.y - 1, parent_mp.y + 2):
            for x in range(parent_mp.x - 1, parent_mp.x + 2):
                if (x, y) in self.is_coord_closed or (x, y) not in MAP_POINT_BY_COORD:
                    continue
                node = self.node_by_coord.get((x, y))
                if node:
                    yield node
                    continue
                if (y == parent_mp.y or x == parent_mp.x or self.allow_diag) and (
                    self.is_neighbor(
                        (mp := MapPoint.from_coords(x, y)), parent_mp, ends
                    )
                ):
                    yield NodeMapPoint(mp=mp)

    def is_neighbor(
        self, mp: MapPoint, parent_mp: MapPoint, ends: set[MapPoint]
    ) -> bool:
        can_move_to_parent = self.data_map_provider.can_mov_to_mp(
            mp,
            parent_mp.cell_id,
            ends,
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
    ) -> float:
        """check cost of move from map point to parent map point"""
        point_weight = self.get_map_point_weight(mp, ends)
        movement_cost: float = (
            DIAG_COST if mp.is_diagonal_move(parent_mp) else HV_COST
        ) * point_weight
        if self.allow_trough_entity:
            is_cell_on_end_column = self.is_cell_on_ends_column(mp, ends)
            is_cell_on_start_column = mp.x + mp.y == start.x + start.y
            is_cell_on_end_line = self.is_cell_on_ends_line(mp, ends)
            is_cell_on_start_line = mp.x - mp.y == start.x - start.y
            if (not is_cell_on_end_column and not is_cell_on_end_line) or (
                not is_cell_on_start_column and not is_cell_on_start_line
            ):
                movement_cost += self.get_heuristic_to_end(mp, ends)
                movement_cost += start.distance_to_map_point(mp)

            if any(mp.x == end.x for end in ends) or any(mp.y == end.y for end in ends):
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

    def get_map_point_weight(self, mp: MapPoint, ends: set[MapPoint]):
        """get weight of map point"""
        if mp in ends:
            return 1

        point_weight: float
        entity_on_cell = self.entity_state.is_entity_actor_on_cell_id(mp.cell_id)
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
                if self.entity_state.is_entity_actor_on_cell_id(side_map_point.cell_id):
                    point_weight += 0.3

        return point_weight

    def build_path(self, start: MapPoint, closest_node: NodeMapPoint):
        path: list[PathElement] = []

        ends = {closest_node.mp}
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
                        ends,
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
                            ends,
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
                            ends,
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
                            ends,
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


if __name__ == "__main__":
    grid_signals = GridSignals()
    path_finding_signals = PathFindingSignals()
    game_info_signals = GameInfoSignals()

    map_state = MapState(grid_signals=grid_signals)
    entity_state = EntityState(grid_signals=grid_signals)
    interactive_state = InteractiveState(grid_signals=grid_signals)
    fight_state = FightState(game_info_signals=game_info_signals)
    player_state = PlayerState(
        map_state=map_state,
        game_info_signals=game_info_signals,
        entity_state=entity_state,
        interactive_state=interactive_state,
    )

    data_map_provider = DataMapProvider(
        entity_state=entity_state,
        player_state=player_state,
        map_state=map_state,
        fight_state=fight_state,
    )
    path_finding = Pathfinding(
        entity_state=entity_state,
        data_map_provider=data_map_provider,
        player_state=player_state,
        map_state=map_state,
        # path_finding_signals=path_finding_signals,
    )

    map_state.map_id = 154010373
    start = MapPoint.from_cell_id(506)

    ends = {MapPoint.from_cell_id(88), MapPoint.from_cell_id(121)}
    ends |= {mp for mp in ends for mp in mp.side_map_points}

    # [28946, 20741, 28918, 28905]
    # should be 28946 20727 20713
    # + check fight
    application = QApplication(sys.argv)
    widget = GridView(
        grid_signals=grid_signals, path_finding_signals=path_finding_signals
    )
    widget.on_new_map_id(map_state.map_id)
    widget.show()

    def _find_path():
        move_path = path_finding.find_path(
            start,
            ends,
            allow_trough_entity=False,
            allow_diag=False,
            heuristic_scale=10,
        )
        icecream.ic(move_path.path, move_path.end)
        key_cells = move_path.get_key_cells()
        print(key_cells)

    thread = Thread(target=_find_path, daemon=True)
    thread.start()

    application.exec()
