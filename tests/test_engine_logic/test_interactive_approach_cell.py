"""The approach cell used before an interactive must match the official client.

`ClientReference` is transcribed from the AS3 source (`RoleplayWorldFrame` handling
`InteractiveElementActivationMessage`, plus `MapPoint.getNearestFreeCellInDirection`) rather than
reusing the production helpers, so a regression in `Pathfinding` shows up as a diff.
"""

import glob
import os
import random
import tempfile

import pytest
from dofus_unity_reader.data_center.map_reader import MapReader
from dofus_unity_reader.game_constants.directions import DirectionsEnum
from dofus_unity_reader.grid.map_point import MAP_POINT_BY_COORD, MapPoint

from src.core.engine.contexts import MapMovementContext
from src.core.engine.movements.map.map_data_adapter import DataMapProvider
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.signals.log_signals import LogSignals
from src.services.debug_recorder import DebugRecorder
from src.services.logging_utils.loggers import BotLogger

# Map 88082184: a "Cueillir" resource on cell 241, another one on cell 257, walls on 242/256.
HARVEST_MAP_ID = 88082184
HARVEST_SKILL_ID = 69
RESOURCE_CELL = 241
OTHER_RESOURCE_CELL = 257
APPROACH_CELL = 269
BLOCKED_NEIGHBOR_CELLS = (242, 256)
# Map 123471361 cell 163: a door sunk into a wall, no approach cell exists for it.
WALL_DOOR_MAP_ID = 123471361
WALL_DOOR_CELL = 163
WALL_DOOR_START_CELL = 300
EXIT_SKILL_ID = 184
# Map 153878786 cell 506: a fishing spot in the water, logged as really fished from cell 451.
FISHING_MAP_ID = 153878786
FISHING_CELL = 506
FISHING_START_CELL = 451
FISHING_SKILL_ID = 124
CELL_COUNT = 560
PLACEHOLDER_CELL = 559


def _make_pathfinding(map_id: int) -> tuple[Pathfinding, DataMapProvider, MapMovementContext]:
    context = MapMovementContext(
        map_id=map_id,
        in_fight=False,
        obstacle_on_cell_id={},
        occupied_cell_ids=frozenset(),
    )
    data_map_provider = DataMapProvider()
    data_map_provider.set_context(context)
    logger = BotLogger(
        log_signals=LogSignals(),
        title="interactive_approach_cell",
        debug_recorder=DebugRecorder(
            file_path=os.path.join(tempfile.gettempdir(), "interactive_approach_cell.debug.jsonl")
        ),
    )
    path_finding = Pathfinding(data_map_provider=data_map_provider, logger=logger)
    return path_finding, data_map_provider, context


class ClientReference:
    """Transcription of the client algorithm, used as the oracle."""

    def __init__(self, data_map_provider: DataMapProvider) -> None:
        self._provider = data_map_provider

    def point_mov(self, x: int, y: int, previous_cell_id: int) -> bool:
        if (x, y) not in MAP_POINT_BY_COORD:
            return False
        return self._provider.can_mov_to_mp(MapPoint.from_coords(x, y), previous_cell_id)

    def nearest_free_cell_in_direction(
        self, source: MapPoint, orientation: int, forbidden: set[int]
    ) -> MapPoint | None:
        cells: list[MapPoint | None] = []
        weights: list[int] = []
        for index in range(8):
            near_mp = source.get_nearest_mp_in_direction(DirectionsEnum(index))
            if near_mp is not None and near_mp.cell_id not in forbidden:
                speed = self._provider.get_cell_data(near_mp.cell_id).speed
                if not self.point_mov(near_mp.x, near_mp.y, source.cell_id):
                    speed = -100
                weights.append(
                    DirectionsEnum.get_distance(DirectionsEnum(index), DirectionsEnum(orientation))
                    + (5 - speed if speed >= 0 else 11 + abs(speed))
                )
            else:
                weights.append(1000)
            cells.append(near_mp)

        best_index = 0
        for index in range(1, 8):
            if weights[index] < weights[best_index] and cells[index] is not None:
                best_index = index

        best = cells[best_index]
        if best is None and self.point_mov(source.x, source.y, source.cell_id):
            return source
        return best

    def forbidden_cells(self, element_mp: MapPoint) -> set[int]:
        forbidden: set[int] = set()
        for index in range(8):
            near_mp = element_mp.get_nearest_mp_in_direction(DirectionsEnum(index))
            if near_mp is None:
                continue
            cell_data = self._provider.get_cell_data(near_mp.cell_id)
            is_forbidden = not cell_data.mov or bool(cell_data.farmCell)
            if not is_forbidden:
                walkable_count = 8
                for sub_index in range(8):
                    sub_mp = near_mp.get_nearest_mp_in_direction(DirectionsEnum(sub_index))
                    if sub_mp is None:
                        continue
                    if not self.point_mov(sub_mp.x, sub_mp.y, near_mp.cell_id) or not (
                        self.point_mov(sub_mp.x - 1, sub_mp.y, near_mp.cell_id)
                        or self.point_mov(sub_mp.x, sub_mp.y - 1, near_mp.cell_id)
                    ):
                        walkable_count -= 1
                is_forbidden = walkable_count == 0
            if is_forbidden:
                forbidden.add(near_mp.cell_id)
        return forbidden

    def destination(self, player_mp: MapPoint, element_mp: MapPoint, minimal_range: int = 1) -> MapPoint:
        forbidden = self.forbidden_cells(element_mp)
        element_cell_data = self._provider.get_cell_data(element_mp.cell_id)
        if element_mp.distance_to_map_point(player_mp) <= minimal_range and (
            not element_cell_data.mov or element_cell_data.farmCell
        ):
            return player_mp

        destination = self.nearest_free_cell_in_direction(
            element_mp, int(element_mp.advanced_orientation_to(player_mp)), forbidden
        )
        for _ in range(minimal_range - 1):
            if destination is None:
                break
            forbidden.add(destination.cell_id)
            destination = self.nearest_free_cell_in_direction(
                destination,
                int(destination.advanced_orientation_to(player_mp, four_dir=False)),
                forbidden,
            )
            if destination is None or destination.cell_id == player_mp.cell_id:
                break

        if destination is None or destination.cell_id in forbidden:
            return element_mp
        return destination


def _walkable_cells(data_map_provider: DataMapProvider) -> list[int]:
    return [
        cell_id
        for cell_id in range(CELL_COUNT)
        if data_map_provider.can_mov_to_mp(MapPoint.from_cell_id(cell_id))
    ]


def test_harvest_from_257_walks_to_269_like_the_client() -> None:
    # Reproduces the logged session: standing on 257, the client walks 257 -> 270 -> 269
    # before using the resource on 241. See RoleplayWorldFrame.as:1179-1274.
    path_finding, _, context = _make_pathfinding(HARVEST_MAP_ID)

    move_path = path_finding.get_interactive_near_path(
        context,
        MapPoint.from_cell_id(OTHER_RESOURCE_CELL),
        MapPoint.from_cell_id(RESOURCE_CELL),
        skill_ids=[HARVEST_SKILL_ID],
    )

    assert move_path is not None
    assert move_path.end.cell_id == APPROACH_CELL
    assert [element.step.cell_id for element in move_path.path] == [OTHER_RESOURCE_CELL, 270]


def test_blocked_neighbors_are_never_used_as_approach_cell() -> None:
    path_finding, data_map_provider, _ = _make_pathfinding(HARVEST_MAP_ID)
    element_mp = MapPoint.from_cell_id(RESOURCE_CELL)

    assert BLOCKED_NEIGHBOR_CELLS[0] in path_finding.get_interactive_forbidden_cell_ids(element_mp)
    assert BLOCKED_NEIGHBOR_CELLS[1] in path_finding.get_interactive_forbidden_cell_ids(element_mp)

    for start_cell in _walkable_cells(data_map_provider):
        destination = path_finding.get_interactive_destination(
            MapPoint.from_cell_id(start_cell), element_mp, skill_ids=[HARVEST_SKILL_ID]
        )
        assert destination.cell_id not in BLOCKED_NEIGHBOR_CELLS


def test_fishing_spot_in_the_water_is_reachable_thanks_to_the_server_range() -> None:
    # The fish sits on water surrounded by water: no approach cell, the path stops 4 cells away.
    # Fishing carries range 10, so the server accepts it; the same spot with a range 1 skill
    # must be refused. Logs confirm 128 accepted fishing interactions between distance 1 and 5.
    path_finding, data_map_provider, context = _make_pathfinding(FISHING_MAP_ID)
    element_mp = MapPoint.from_cell_id(FISHING_CELL)
    player_mp = MapPoint.from_cell_id(FISHING_START_CELL)

    assert not data_map_provider.get_cell_data(FISHING_CELL).mov
    assert len(path_finding.get_interactive_forbidden_cell_ids(element_mp)) == 8

    fishing = path_finding.get_interactive_near_path(
        context, player_mp, element_mp, skill_ids=[FISHING_SKILL_ID]
    )
    assert fishing is not None
    assert fishing.end.distance_to_map_point(element_mp) == 4

    assert (
        path_finding.get_interactive_near_path(context, player_mp, element_mp, skill_ids=[HARVEST_SKILL_ID])
        is None
    )


def test_refuses_an_element_beyond_the_server_range() -> None:
    # Map 123471361 cell 163: a door sunk into a wall, no approach cell either, but skill 184
    # has range 1 while the path stops 4 cells away. The server would refuse, so we do not try.
    path_finding, _, context = _make_pathfinding(WALL_DOOR_MAP_ID)
    element_mp = MapPoint.from_cell_id(WALL_DOOR_CELL)
    player_mp = MapPoint.from_cell_id(WALL_DOOR_START_CELL)

    assert (
        path_finding.get_interactive_destination(player_mp, element_mp, skill_ids=[EXIT_SKILL_ID]).cell_id
        == WALL_DOOR_CELL
    )

    assert (
        path_finding.get_interactive_near_path(context, player_mp, element_mp, skill_ids=[EXIT_SKILL_ID])
        is None
    )


def test_map_transitions_ignore_the_server_range() -> None:
    # Their element cell comes from the world graph, too unreliable to measure a distance
    # against, so EdgeBehavior opts out and lets the server answer.
    path_finding, _, context = _make_pathfinding(WALL_DOOR_MAP_ID)

    move_path = path_finding.get_interactive_near_path(
        context,
        MapPoint.from_cell_id(WALL_DOOR_START_CELL),
        MapPoint.from_cell_id(WALL_DOOR_CELL),
        skill_ids=[EXIT_SKILL_ID],
        ignore_server_range=True,
    )

    assert move_path is not None
    assert move_path.end.cell_id != WALL_DOOR_CELL


def test_an_unreachable_approach_cell_is_refused_even_without_the_range_check() -> None:
    # `ignore_server_range` must not become a blanket "interact from anywhere": it only covers
    # elements that have no approach cell. When one exists, both regimes agree.
    path_finding, _, context = _make_pathfinding(HARVEST_MAP_ID)
    args = (
        context,
        MapPoint.from_cell_id(OTHER_RESOURCE_CELL),
        MapPoint.from_cell_id(RESOURCE_CELL),
    )

    strict = path_finding.get_interactive_near_path(*args, skill_ids=[HARVEST_SKILL_ID])
    lenient = path_finding.get_interactive_near_path(
        *args, skill_ids=[HARVEST_SKILL_ID], ignore_server_range=True
    )

    assert strict is not None and lenient is not None
    assert strict.end.cell_id == lenient.end.cell_id == APPROACH_CELL


def test_standing_on_the_resource_cell_leaves_toward_down_right() -> None:
    # Logged client behaviour: on cell 257, clicking the resource of cell 257 walks to 271.
    path_finding, _, _ = _make_pathfinding(HARVEST_MAP_ID)
    element_mp = MapPoint.from_cell_id(OTHER_RESOURCE_CELL)

    destination = path_finding.get_interactive_destination(
        element_mp, element_mp, skill_ids=[HARVEST_SKILL_ID]
    )

    assert destination.cell_id == 271


def _map_ids_sample(count: int) -> list[int]:
    map_files = glob.glob("DBDofusUnity/datas/bundles/map/map_*.json")
    map_ids = sorted(int(os.path.basename(path)[len("map_") : -len(".json")]) for path in map_files)
    if not map_ids:
        pytest.skip("map bundles are not extracted")
    rng = random.Random(7)
    return rng.sample(map_ids, min(count, len(map_ids)))


@pytest.mark.parametrize("map_id", [HARVEST_MAP_ID, *_map_ids_sample(6)])
def test_destination_matches_the_client_on_every_cell_of_the_map(map_id: int) -> None:
    path_finding, data_map_provider, _ = _make_pathfinding(map_id)
    reference = ClientReference(data_map_provider)

    element_cells = sorted(
        {
            ref.cellId
            for ref in MapReader().map_by_id(map_id).references
            if ref.m_interactionId is not None and ref.cellId is not None and ref.cellId != PLACEHOLDER_CELL
        }
    )
    walkable_cells = _walkable_cells(data_map_provider)

    divergences: list[tuple[int, int, int, int]] = []
    for element_cell in element_cells:
        element_mp = MapPoint.from_cell_id(element_cell)
        for start_cell in walkable_cells:
            if start_cell == element_cell:
                continue
            player_mp = MapPoint.from_cell_id(start_cell)
            expected = reference.destination(player_mp, element_mp).cell_id
            actual = path_finding.get_interactive_destination(
                player_mp, element_mp, skill_ids=[HARVEST_SKILL_ID]
            ).cell_id
            if expected != actual:
                divergences.append((start_cell, element_cell, expected, actual))

    assert not divergences, f"{len(divergences)} divergences, first: {divergences[:5]}"
