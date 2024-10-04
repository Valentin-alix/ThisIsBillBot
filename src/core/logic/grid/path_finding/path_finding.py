import heapq
from dataclasses import dataclass, field

from icecream import icecream

from src.core.logic.grid.data_map_provider import DataMapProvider
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.map_tools import MapTools
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_element import PathElement
from src.core.repositories.data_reader import DataReader
from src.core.repositories.map_reader import MapReader
from src.core.states.entity_state import EntityState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.signals.player_signals import StatePropertySignals

HV_COST: int = 10
DIAG_COST: int = 15
HEURISTIC_SCALE: int = 10
INFINITE_COST: float = float("inf")


@dataclass
class Pathfinding:
    data_map_provider: DataMapProvider
    player_state: PlayerState
    map_state: MapState
    parent_of_cell: dict[int, int] = field(init=False, default_factory=lambda: {})
    cost_of_cell_by_id: dict[int, float] = field(init=False, default_factory=lambda: {})
    is_cell_closed: set = field(init=False, default_factory=set)
    is_entity_on_cell_by_id: dict[int, bool] = field(
        init=False, default_factory=lambda: {}
    )
    open_list: list[tuple[float, int]] = field(init=False, default_factory=lambda: [])

    def get_near_path_to_interactive(
        self, element_id: int, skill_id: int
    ) -> MovementPath | None:
        skill_range = DataReader().skill_by_id[skill_id].range

        cell_id_element = (
            MapReader()
            .get_ref_data_by_element_id(self.map_state.map.map_id)[element_id]
            .cellId
        )
        mp_element = MapPoint.from_cell_id(cell_id_element)

        move_path = self.find_path(self.player_state.map_point, mp_element)
        if move_path.end.point.distance_to_point(mp_element.point) > skill_range:
            return None

        if skill_range == 1:
            for path in reversed(move_path.path.copy()):
                if path.step.point.distance_to_point(mp_element.point) > skill_range:
                    break
                move_path.end = move_path.path.pop().step

        return move_path

    def find_path(
        self,
        start: MapPoint,
        end: MapPoint,
        allow_diag: bool = True,
        allow_trough_entity: bool = True,
        avoid_obstacles: bool = True,
        cells_blacklist: list[int] | None = None,
    ) -> MovementPath:
        if cells_blacklist is None:
            cells_blacklist = []

        self.parent_of_cell.clear()
        self.is_cell_closed.clear()
        self.is_entity_on_cell_by_id.clear()
        self.cost_of_cell_by_id.clear()
        self.open_list.clear()
        self.cost_of_cell_by_id[start.cell_id] = 0

        end_cell_aux_id = start.cell_id
        dist_to_end = end.distance_to_cell_id(start.cell_id)
        self.data_map_provider.fill_entity_on_cell_array(
            self.is_entity_on_cell_by_id, allow_trough_entity
        )

        heapq.heappush(self.open_list, (0, start.cell_id))
        while self.open_list:
            _, parent_id = heapq.heappop(self.open_list)
            if parent_id in self.is_cell_closed:
                continue
            self.is_cell_closed.add(parent_id)
            for x, y in self.iter_childs(
                parent_id,
                end,
                allow_trough_entity,
                avoid_obstacles,
                allow_diag,
            ):
                mp = MapPoint.from_coords(x, y)
                move_cost = self.move_cost(
                    allow_trough_entity,
                    start,
                    end,
                    x,
                    y,
                    parent_id,
                )
                cell_id = mp.cell_id
                if cell_id in cells_blacklist:
                    continue
                if allow_trough_entity:
                    dist_tmp_to_end = end.distance_to_cell_id(mp.cell_id)
                    if dist_tmp_to_end < dist_to_end:
                        end_cell_aux_id = cell_id
                        dist_to_end = dist_tmp_to_end
                if (
                    cell_id not in self.parent_of_cell
                    or move_cost < self.cost_of_cell_by_id[cell_id]
                ):
                    self.parent_of_cell[cell_id] = parent_id
                    self.cost_of_cell_by_id[cell_id] = move_cost
                    heuristic = HEURISTIC_SCALE * (
                        abs(end.point.x - x) + abs(end.point.y - y)
                    )
                    total_cost = heuristic + move_cost
                    heapq.heappush(self.open_list, (total_cost, cell_id))
        mov_path = self.build_path(
            allow_trough_entity,
            allow_diag,
            avoid_obstacles,
            end_cell_aux_id,
            start,
            end,
        )
        return mov_path

    def iter_childs(
        self,
        parent_id: int,
        end: MapPoint,
        allow_through_entity: bool,
        avoid_obstacles: bool,
        allow_diag: bool,
    ):
        parent_x = MapTools.get_cell_x_by_id(parent_id)
        parent_y = MapTools.get_cell_y_by_id(parent_id)
        for y in range(parent_y - 1, parent_y + 2):
            for x in range(parent_x - 1, parent_x + 2):
                if self.is_child(
                    end,
                    allow_through_entity,
                    avoid_obstacles,
                    allow_diag,
                    x,
                    y,
                    parent_id,
                ):
                    yield x, y

    def is_child(
        self,
        end: MapPoint,
        allow_through_entity: bool,
        avoid_obstacles: bool,
        allow_diag: bool,
        x: int,
        y: int,
        parent_id: int,
    ) -> bool:
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        parent_x = MapTools.get_cell_x_by_id(parent_id)
        parent_y = MapTools.get_cell_y_by_id(parent_id)
        can_move_from_parent_to_end = self.data_map_provider.can_mov(
            x,
            y,
            allow_through_entity,
            parent_id,
            end.cell_id,
            avoid_obstacles,
        )
        return (
            cell_id is not None
            and cell_id not in self.is_cell_closed
            and cell_id != parent_id
            and can_move_from_parent_to_end
            and (
                y == parent_y
                or x == parent_x
                or allow_diag
                and (
                    self.data_map_provider.can_mov(
                        parent_x,
                        y,
                        allow_through_entity,
                        parent_id,
                    )
                    or self.data_map_provider.can_mov(
                        x,
                        parent_y,
                        allow_through_entity,
                        parent_id,
                    )
                )
            )
        )

    def move_cost(
        self,
        allow_thought_entity: bool,
        start: MapPoint,
        end: MapPoint,
        x: int,
        y: int,
        parent_id: int,
    ):
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        point_weight = self.get_map_point_weight(allow_thought_entity, end, x, y)
        parent_x = MapTools.get_cell_x_by_id(parent_id)
        parent_y = MapTools.get_cell_y_by_id(parent_id)
        movement_cost = (
            self.cost_of_cell_by_id[parent_id]
            + (HV_COST if y == parent_y or x == parent_x else DIAG_COST) * point_weight
        )
        if allow_thought_entity:
            cell_on_end_column = x + y == start.point.y + end.point.y
            cell_on_start_column = x + y == start.point.x + start.point.y
            cell_on_end_line = x - y == end.point.x - end.point.y
            cell_on_start_line = x - y == start.point.x - start.point.y
            if (
                not cell_on_end_column
                and not cell_on_end_line
                or not cell_on_start_column
                and not cell_on_start_line
            ):
                movement_cost += end.distance_to_cell_id(cell_id)
                movement_cost += start.distance_to_cell_id(cell_id)
            if x == end.point.x or y == end.point.y:
                movement_cost -= 3
            if (
                cell_on_end_column
                or cell_on_end_line
                or x + y == parent_x + parent_y
                or x - y == parent_x - parent_y
            ):
                movement_cost -= 2
            if x == start.point.x or y == start.point.y:
                movement_cost -= 3
            if cell_on_start_column or cell_on_start_line:
                movement_cost -= 2
        return movement_cost

    def get_map_point_weight(
        self,
        allow_trough_entity: bool,
        end: MapPoint,
        x: int,
        y: int,
    ):
        cell_id = MapTools.get_cell_id_by_coord(x, y)
        if cell_id == end.cell_id:
            return 1
        point_weight: float
        speed = self.data_map_provider.get_cell_data(cell_id)["speed"]
        entity_on_cell = self.is_entity_on_cell_by_id.get(cell_id)
        if allow_trough_entity:
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
            for dx, dy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                if MapTools.is_valid_coord(
                    x + dx, y + dy
                ) and self.is_entity_on_cell_by_id.get(
                    MapTools.get_cell_id_by_coord(x + dx, y + dy)
                ):
                    point_weight += 0.3

        return point_weight

    def build_path(
        self,
        allow_though_entity: bool,
        allow_diag: bool,
        avoid_obstacles: bool,
        end_cell_aux_id: int,
        start: MapPoint,
        end: MapPoint,
    ):
        path: list[PathElement] = []

        cursor = end.cell_id
        if self.parent_of_cell.get(end.cell_id) is None:
            cursor = end_cell_aux_id
            mov_path_end = MapPoint.from_cell_id(end_cell_aux_id)
        else:
            mov_path_end = end

        while cursor != start.cell_id:
            if allow_diag:
                parent = self.parent_of_cell.get(cursor)
                grand_parent = self.parent_of_cell.get(parent) if parent else None
                grand_grand_parent = (
                    self.parent_of_cell.get(grand_parent) if grand_parent else None
                )
                k_x = MapTools.get_cell_x_by_id(cursor)
                k_y = MapTools.get_cell_y_by_id(cursor)
                if (
                    grand_parent is not None
                    and MapTools.get_distance(cursor, grand_parent) == 1
                ):
                    if self.data_map_provider.can_mov(
                        k_x,
                        k_y,
                        allow_though_entity,
                        grand_parent,
                        end.cell_id,
                        avoid_obstacles,
                    ):
                        self.parent_of_cell[cursor] = grand_parent
                elif (
                    grand_grand_parent is not None
                    and MapTools.get_distance(cursor, grand_grand_parent) == 2
                ):
                    next_x = MapTools.get_cell_x_by_id(grand_grand_parent)
                    next_y = MapTools.get_cell_y_by_id(grand_grand_parent)
                    inter_x = k_x + round((next_x - k_x) / 2)
                    inter_y = k_y + round((next_y - k_y) / 2)

                    if (
                        self.data_map_provider.can_mov(
                            inter_x,
                            inter_y,
                            allow_though_entity,
                            cursor,
                            end.cell_id,
                            avoid_obstacles,
                        )
                        and self.data_map_provider.get_point_weight(inter_x, inter_y)
                        < 2
                    ):
                        self.parent_of_cell[cursor] = MapTools.get_cell_id_by_coord(
                            inter_x, inter_y
                        )
                elif (
                    grand_parent is not None
                    and MapTools.get_distance(cursor, grand_parent) == 2
                ):
                    next_x = MapTools.get_cell_x_by_id(grand_parent)
                    next_y = MapTools.get_cell_y_by_id(grand_parent)
                    inter_x = MapTools.get_cell_x_by_id(parent)
                    inter_y = MapTools.get_cell_y_by_id(parent)
                    if (
                        k_x + k_y == next_x + next_y
                        and k_x - k_y != inter_x - inter_y
                        and not self.data_map_provider.is_change_zone(
                            MapTools.get_cell_id_by_coord(k_x, k_y),
                            MapTools.get_cell_id_by_coord(inter_x, inter_y),
                        )
                        and not self.data_map_provider.is_change_zone(
                            MapTools.get_cell_id_by_coord(inter_x, inter_y),
                            MapTools.get_cell_id_by_coord(next_x, next_y),
                        )
                    ):
                        self.parent_of_cell[cursor] = grand_parent
                    elif (
                        k_x - k_y == next_x - next_y
                        and k_x - k_y != inter_x - inter_y
                        and not self.data_map_provider.is_change_zone(
                            MapTools.get_cell_id_by_coord(k_x, k_y),
                            MapTools.get_cell_id_by_coord(inter_x, inter_y),
                        )
                        and not self.data_map_provider.is_change_zone(
                            MapTools.get_cell_id_by_coord(inter_x, inter_y),
                            MapTools.get_cell_id_by_coord(next_x, next_y),
                        )
                    ):
                        self.parent_of_cell[cursor] = grand_parent

                    elif (
                        k_x == next_x
                        and k_x != inter_x
                        and self.data_map_provider.get_point_weight(k_x, inter_y) < 2
                        and self.data_map_provider.can_mov(
                            k_x,
                            inter_y,
                            allow_though_entity,
                            cursor,
                            end.cell_id,
                            avoid_obstacles,
                        )
                    ):
                        self.parent_of_cell[cursor] = MapTools.get_cell_id_by_coord(
                            k_x, inter_y
                        )

                    elif (
                        k_y == next_y
                        and k_y != inter_y
                        and self.data_map_provider.get_point_weight(inter_x, k_y) < 2
                        and self.data_map_provider.can_mov(
                            inter_x,
                            k_y,
                            allow_though_entity,
                            cursor,
                            end.cell_id,
                            avoid_obstacles,
                        )
                    ):
                        self.parent_of_cell[cursor] = MapTools.get_cell_id_by_coord(
                            inter_x, k_y
                        )
            path.append(
                PathElement(
                    MapPoint.from_cell_id(self.parent_of_cell[cursor]),
                    MapTools.get_look_direction8_exact(
                        self.parent_of_cell[cursor], cursor
                    ),
                )
            )
            cursor = self.parent_of_cell[cursor]

        mov_path: MovementPath = MovementPath(start, mov_path_end, path)
        mov_path.path.reverse()
        return mov_path


if __name__ == "__main__":
    map_id = 190579712
    start = MapPoint.from_cell_id(341)
    end = MapPoint.from_cell_id(91)

    is_in_fight = False

    state_property_signals = StatePropertySignals()
    map_state = MapState(state_property_signals=state_property_signals)
    entity_state = EntityState(state_property_signals=state_property_signals)
    player_state = PlayerState(
        map_state=map_state, state_property_signals=StatePropertySignals()
    )
    map_state.map.map_id = map_id

    data_map_provider = DataMapProvider(
        entity_state=entity_state, player_state=player_state, map_state=map_state
    )
    path_finding = Pathfinding(
        data_map_provider=data_map_provider,
        player_state=player_state,
        map_state=map_state,
    )

    temp = path_finding.find_path(
        start,
        end,
        allow_diag=not is_in_fight,
        allow_trough_entity=not is_in_fight,
        avoid_obstacles=True,
    )
    icecream.ic(temp.path, temp.end)

    ans = temp.get_key_cells()

    # should be 24917 28873 24723 24695

    print(ans)
