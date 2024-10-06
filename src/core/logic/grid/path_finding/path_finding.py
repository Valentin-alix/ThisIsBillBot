import heapq
from dataclasses import dataclass, field
from typing import Iterator

import icecream

from src.common.debugger import timeit
from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
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
from src.signals.player_signals import StatePropertySignals

HV_COST: int = 10
DIAG_COST: int = 15
HEURISTIC_SCALE: int = 10


@dataclass
class Pathfinding:
    data_map_provider: DataMapProvider
    player_state: PlayerState
    map_state: MapState
    entity_state: EntityState

    allow_diag: bool = field(init=False, default=True)
    allow_trough_entity: bool = field(init=False, default=True)
    avoid_obstacles: bool = field(init=False, default=True)
    heuristic_scale: int = field(init=False, default=HEURISTIC_SCALE)

    node_by_coord: dict[tuple[int, int], NodeMapPoint] = field(
        init=False, default_factory=dict
    )
    open_list: list[NodeMapPoint] = field(init=False, default_factory=list)
    is_coord_closed: set[tuple[int, int]] = field(init=False, default_factory=set)

    def get_near_path_to_interactive(
        self, element_id: int, skill_id: int
    ) -> MovementPath | None:
        skill_range = DataReader().skill_by_id[skill_id].range

        cell_id_element = (
            MapReader()
            .get_ref_data_by_element_id(self.map_state.map_id)[element_id]
            .cellId
        )
        mp_element = MapPoint.from_cell_id(cell_id_element)

        move_path = self.find_path(
            self.player_state.map_point, mp_element, stop_at_side=True
        )
        if move_path.end.point.distance_to_point(mp_element.point) > skill_range:
            return None

        return move_path

    @timeit
    def find_path(
        self,
        start: MapPoint,
        end: MapPoint,
        allow_diag: bool = True,
        allow_trough_entity: bool = True,
        avoid_obstacles: bool = True,
        heuristic_scale: int = HEURISTIC_SCALE,
        stop_at_side: bool = False,
    ) -> MovementPath:
        self.allow_diag = allow_diag
        self.allow_trough_entity = allow_trough_entity
        self.avoid_obstacles = avoid_obstacles
        self.heuristic_scale = heuristic_scale

        self.open_list.clear()
        self.node_by_coord.clear()
        self.is_coord_closed.clear()

        dist_to_end = self.get_heuristic_to_end(start, end)
        start_node = NodeMapPoint(
            mp=start,
            cost_to_node=0,
            cost_to_end=dist_to_end,
            total_cost=dist_to_end,
            parent=None,
        )

        closest_node: NodeMapPoint = start_node

        heapq.heappush(self.open_list, start_node)

        iteration = 0
        while self.open_list:
            iteration += 1
            curr_node = heapq.heappop(self.open_list)
            if self.is_goal_reached(stop_at_side, curr_node, end):
                closest_node = curr_node
                break
            curr_node.in_open_set = False
            self.is_coord_closed.add((curr_node.mp.point.x, curr_node.mp.point.y))
            for node in self.get_neighbors(curr_node.mp, end):
                cost_to_node = (
                    self.get_move_cost(node.mp, curr_node.mp, start, end)
                    + curr_node.cost_to_node
                )

                if node.cost_to_node < cost_to_node:
                    continue

                cost_to_end: float = self.get_heuristic_to_end(node.mp, end)
                node.cost_to_node = cost_to_node
                node.parent = curr_node
                node.cost_to_end = cost_to_end
                node.total_cost = HEURISTIC_SCALE * cost_to_end + cost_to_node

                if node.cost_to_end < closest_node.cost_to_end:
                    closest_node = node

                self.node_by_coord[(node.mp.point.x, node.mp.point.y)] = node

                if not node.in_open_set:
                    heapq.heappush(self.open_list, node)
                    node.in_open_set = True

        mov_path = self.build_path(start, closest_node)
        return mov_path

    def get_heuristic_to_end(self, mp: MapPoint, end: MapPoint) -> float:
        return end.distance_to_cell_id(mp.cell_id)

    def is_goal_reached(
        self, stop_at_side: bool, curr_node: NodeMapPoint, end: MapPoint
    ):
        if stop_at_side:
            return (
                curr_node.mp.cell_id == end.cell_id
                or curr_node.mp.point in end.point.get_side_points
            )
        return curr_node.mp.cell_id == end.cell_id

    def get_neighbors(
        self, parent_mp: MapPoint, end: MapPoint
    ) -> Iterator[NodeMapPoint]:
        for y in range(parent_mp.point.y - 1, parent_mp.point.y + 2):
            for x in range(parent_mp.point.x - 1, parent_mp.point.x + 2):
                if (x, y) in self.is_coord_closed:
                    continue
                node = self.node_by_coord.get((x, y))
                if node:
                    yield node
                    continue
                if (
                    y == parent_mp.point.y or x == parent_mp.point.x or self.allow_diag
                ) and (
                    self.is_neighbor((mp := MapPoint.from_coords(x, y)), parent_mp, end)
                ):
                    yield NodeMapPoint(mp=mp)
                else:
                    self.is_coord_closed.add((x, y))

    def is_neighbor(self, mp: MapPoint, parent_mp: MapPoint, end: MapPoint) -> bool:
        can_move_to_parent = self.data_map_provider.can_mov_to_mp(
            mp,
            parent_mp.cell_id,
            end,
            allow_through_entity=self.allow_trough_entity,
            avoid_obstacle=self.avoid_obstacles,
        )
        return can_move_to_parent and (
            self.data_map_provider.can_mov_to_mp(
                MapPoint.from_coords(parent_mp.point.x, mp.point.y),
                parent_mp.cell_id,
                allow_through_entity=self.allow_trough_entity,
                avoid_obstacle=self.avoid_obstacles,
            )
            or self.data_map_provider.can_mov_to_mp(
                MapPoint.from_coords(mp.point.x, parent_mp.point.y),
                parent_mp.cell_id,
                allow_through_entity=self.allow_trough_entity,
                avoid_obstacle=self.avoid_obstacles,
            )
        )

    def get_move_cost(
        self,
        mp: MapPoint,
        parent_mp: MapPoint,
        start: MapPoint,
        end: MapPoint,
    ) -> float:
        """check cost of move from map point to parent map point"""
        point_weight = self.get_map_point_weight(mp, end)
        movement_cost: float = (
            DIAG_COST if mp.point.is_diagonal_move(parent_mp.point) else HV_COST
        ) * point_weight
        if self.allow_trough_entity:
            is_cell_on_end_column = mp.point.x + mp.point.y == end.point.y + end.point.y
            is_cell_on_start_column = (
                mp.point.x + mp.point.y == start.point.x + start.point.y
            )
            is_cell_on_end_line = mp.point.x - mp.point.y == end.point.x - end.point.y
            is_cell_on_start_line = (
                mp.point.x - mp.point.y == start.point.x - start.point.y
            )
            if (not is_cell_on_end_column and not is_cell_on_end_line) or (
                not is_cell_on_start_column and not is_cell_on_start_line
            ):
                movement_cost += self.get_heuristic_to_end(mp, end)
                movement_cost += start.distance_to_cell_id(mp.cell_id)

            if mp.point.x == end.point.x or mp.point.y == end.point.y:
                movement_cost -= 3

            if (
                is_cell_on_end_column
                or is_cell_on_end_line
                or mp.point.x + mp.point.y == parent_mp.point.x + parent_mp.point.y
                or mp.point.x - mp.point.y == parent_mp.point.x - parent_mp.point.y
            ):
                movement_cost -= 2

            if mp.point.x == start.point.x or mp.point.y == start.point.y:
                movement_cost -= 3

            if is_cell_on_start_column or is_cell_on_start_line:
                movement_cost -= 2

        return movement_cost

    def get_map_point_weight(self, mp: MapPoint, end: MapPoint):
        """get weight of map point"""
        if mp.cell_id == end.cell_id:
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
            for side_point in mp.point.get_side_points:
                if MapTools.is_valid_coord(
                    side_point.x, side_point.y
                ) and self.entity_state.is_entity_actor_on_cell_id(
                    MapTools.get_cell_id_by_coord(side_point.x, side_point.y)
                ):
                    point_weight += 0.3

        return point_weight

    def build_path(self, start: MapPoint, closest_node: NodeMapPoint):
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
                        closest_node.mp,
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
                    inter_x = cursor.mp.point.x + round(
                        (grand_grand_parent.mp.point.x - cursor.mp.point.x) / 2
                    )
                    inter_y = cursor.mp.point.y + round(
                        (grand_grand_parent.mp.point.y - cursor.mp.point.y) / 2
                    )

                    inter_mp = MapPoint.from_coords(inter_x, inter_y)
                    if (
                        self.data_map_provider.can_mov_to_mp(
                            inter_mp,
                            cursor.mp.cell_id,
                            closest_node.mp,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                        and self.data_map_provider.get_point_weight(
                            inter_mp, self.allow_trough_entity
                        )
                        < 2
                    ):
                        cursor.parent = self.node_by_coord[inter_mp.cell_id]
                elif (
                    grand_parent is not None
                    and MapTools.get_distance(
                        cursor.mp.cell_id, grand_parent.mp.cell_id
                    )
                    == 2
                ):
                    assert parent is not None

                    if (
                        cursor.mp.point.x + cursor.mp.point.y
                        == grand_parent.mp.point.x + grand_parent.mp.point.y
                        and cursor.mp.point.x - cursor.mp.point.y
                        != parent.mp.point.x - parent.mp.point.y
                        and not self.data_map_provider.is_changing_zone(
                            cursor.mp.cell_id, parent.mp.cell_id
                        )
                        and not self.data_map_provider.is_changing_zone(
                            parent.mp.cell_id, grand_parent.mp.cell_id
                        )
                    ):
                        cursor.parent = grand_parent
                    elif (
                        cursor.mp.point.x - cursor.mp.point.y
                        == grand_parent.mp.point.x - grand_parent.mp.point.y
                        and cursor.mp.point.x - cursor.mp.point.y
                        != parent.mp.point.x - parent.mp.point.y
                        and not self.data_map_provider.is_changing_zone(
                            cursor.mp.cell_id, parent.mp.cell_id
                        )
                        and not self.data_map_provider.is_changing_zone(
                            parent.mp.cell_id, grand_parent.mp.cell_id
                        )
                    ):
                        cursor.parent = grand_parent

                    elif (
                        cursor.mp.point.x == grand_parent.mp.point.x
                        and cursor.mp.point.x != parent.mp.point.x
                        and self.data_map_provider.get_point_weight(
                            MapPoint.from_coords(cursor.mp.point.x, parent.mp.point.y),
                            self.allow_trough_entity,
                        )
                        < 2
                        and self.data_map_provider.can_mov_to_mp(
                            MapPoint.from_coords(cursor.mp.point.x, parent.mp.point.y),
                            cursor.mp.cell_id,
                            closest_node.mp,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                    ):
                        cursor.parent = self.node_by_coord[
                            MapTools.get_cell_id_by_coord(
                                cursor.mp.point.x, parent.mp.point.y
                            )
                        ]

                    elif (
                        cursor.mp.point.y == grand_parent.mp.point.y
                        and cursor.mp.point.y != parent.mp.point.y
                        and self.data_map_provider.get_point_weight(
                            MapPoint.from_coords(parent.mp.point.x, cursor.mp.point.y),
                            self.allow_trough_entity,
                        )
                        < 2
                        and self.data_map_provider.can_mov_to_mp(
                            MapPoint.from_coords(parent.mp.point.x, cursor.mp.point.y),
                            cursor.mp.cell_id,
                            closest_node.mp,
                            allow_through_entity=self.allow_trough_entity,
                            avoid_obstacle=self.avoid_obstacles,
                        )
                    ):
                        cursor.parent = self.node_by_coord[
                            MapTools.get_cell_id_by_coord(
                                parent.mp.point.x, cursor.mp.point.y
                            )
                        ]
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

    map_id = 153878786

    start = MapPoint.from_cell_id(124)
    ends = [
        MapPoint.from_coords(point.x, point.y)
        for point in MapPoint.from_cell_id(423).point.get_side_points
    ]
    end = MapPoint.from_cell_id(423)

    is_in_fight = False

    state_property_signals = StatePropertySignals()
    map_state = MapState(state_property_signals=state_property_signals)
    entity_state = EntityState(state_property_signals=state_property_signals)
    interactive_state = InteractiveState(state_property_signals=state_property_signals)
    fight_state = FightState(state_property_signals=state_property_signals)
    player_state = PlayerState(
        map_state=map_state,
        state_property_signals=StatePropertySignals(),
        entity_state=entity_state,
        interactive_state=interactive_state,
        fight_state=fight_state,
    )
    map_state.map_id = map_id

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
    )

    temp = path_finding.find_path(
        start,
        end,
        allow_diag=not is_in_fight,
        allow_trough_entity=not is_in_fight,
    )
    icecream.ic(temp.path, temp.end)

    # should be:
    #   - 16827: 526/7
    #   - 16826: 499/6
    #   - 24907: 331/6

    # we have:
    #   - 29185: 513/7
    #   - 25047: 471/6
    #   - 24907: 331/6

    ans = temp.get_key_cells()

    print(ans)
