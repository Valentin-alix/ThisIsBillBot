from datetime import datetime

import pytest

from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.game_constants.map_capability import MapCapabilityFlag
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import FORBIDDEN_MAP_IDS
from DBDofusUnity.dofus_unity_reader.models.datas.map_positions_root import MapInformationRootItem
from DBDofusUnity.dofus_unity_reader.models.world_graph import (
    Edge,
    OutgoingEdge,
    Transition,
    Vertice,
    WorldGraphData,
)

from src.core.engine.contexts import CriterionContext, WorldPathContext, WorldTransitionContext
from src.core.engine.movements.world import astar_vertice
from src.core.engine.movements.world.astar_allow_capability import AstarAllowHavreSac
from src.core.engine.movements.world.astar_vertice import AstarWorld
from src.core.engine.movements.world.edge import iter_valid_outgoing_edges


def _context() -> WorldTransitionContext:
    return WorldTransitionContext(
        criterion=CriterionContext(
            is_sub=True,
            player_level=200,
            player_limited_level=200,
            player_subscription_end_date=datetime.now(),
            player_jobs_lvl_by_id={},
            player_waypoint_map_ids=frozenset(),
            player_server_id=0,
            player_character_id=0,
            map_id=0,
            sub_area_id=0,
            fight_breed_id=0,
            fight_characteristic_by_id={},
            inventory_objects_by_uid={},
            positive_actor_count=0,
        ),
        forbidden_edge_transitions=frozenset(),
    )


def test_forbidden_map_ids_are_excluded_from_outgoing_edges(monkeypatch: pytest.MonkeyPatch) -> None:
    forbidden_map_id = next(iter(FORBIDDEN_MAP_IDS))
    origin = Vertice(m_mapId=1, m_zoneId=1, m_uid=1)
    blocked_edge = Edge(
        m_from=origin,
        m_to=Vertice(m_mapId=forbidden_map_id, m_zoneId=1, m_uid=2),
        m_transitions=[Transition(1, 0, -1, "", forbidden_map_id, 0, -1)],
    )
    allowed_edge = Edge(
        m_from=origin,
        m_to=Vertice(m_mapId=999999, m_zoneId=1, m_uid=3),
        m_transitions=[Transition(1, 0, -1, "", 999999, 0, -1)],
    )
    def fake_get_outgoing_edges_from_vertex(self: WorldGraphReader, vertex: Vertice) -> list[Edge]:
        return [blocked_edge, allowed_edge]

    monkeypatch.setattr(
        WorldGraphReader, "get_outgoing_edges_from_vertex", fake_get_outgoing_edges_from_vertex
    )

    edges = list(iter_valid_outgoing_edges(origin, _context()))

    assert edges == [allowed_edge]


@pytest.fixture
def small_world(monkeypatch: pytest.MonkeyPatch) -> tuple[WorldPathContext, list[Vertice], list[Edge]]:
    vertices = [Vertice(m_mapId=999_991 + index, m_zoneId=1, m_uid=index) for index in range(4)]
    edges = [
        Edge(
            m_from=vertices[index],
            m_to=vertices[index + 1],
            m_transitions=[Transition(1, 0, -1, "", vertices[index + 1].m_mapId, 0, -1)],
        )
        for index in range(2)
    ]
    graph = WorldGraphData(
        m_vertices={vertex.m_mapId: {1: vertex} for vertex in vertices},
        m_edges={edge.m_from.m_uid: {edge.m_to.m_uid: edge} for edge in edges},
        m_outgoingEdges={edge.m_from.m_uid: OutgoingEdge(m_edgeList=[edge]) for edge in edges},
    )
    map_positions = {
        vertex.m_mapId: MapInformationRootItem(
            id=vertex.m_mapId,
            m_flags=int(MapCapabilityFlag.ALLOW_TELEPORT_TO) if index == 1 else 0,
            posX=index,
            posY=0,
            nameId=0,
            subAreaId=0,
            worldMap=0,
            tacticalModeTemplateId=0,
        )
        for index, vertex in enumerate(vertices)
    }
    monkeypatch.setitem(vars(WorldGraphReader()), "datas", graph)
    monkeypatch.setitem(vars(DataReader()), "map_info_by_map_id", map_positions)

    def distance(current: MapInformationRootItem, ends: list[MapInformationRootItem]) -> float:
        return min(abs(current.posX - end.posX) for end in ends)

    monkeypatch.setattr(astar_vertice, "get_dist_to_maps", distance)
    context = WorldPathContext(transition=_context(), current_map_pos=map_positions[vertices[0].m_mapId])
    return context, vertices, edges


@pytest.mark.parametrize(("destination", "reachable"), [(2, True), (0, True), (3, False)])
def test_world_path_reconstructs_edges_or_reports_no_route(
    small_world: tuple[WorldPathContext, list[Vertice], list[Edge]],
    destination: int,
    reachable: bool,
) -> None:
    context, vertices, edges = small_world
    search = AstarWorld()
    search.set_context(context)

    path = search.find_path(vertices[0], {vertices[destination]})

    assert path == (edges[:destination] if reachable else None)


def test_haven_bag_search_stops_at_a_teleportable_map(
    small_world: tuple[WorldPathContext, list[Vertice], list[Edge]],
) -> None:
    context, vertices, edges = small_world
    search = AstarAllowHavreSac()
    search.set_context(context)

    path = search.find_path(vertices[0], {vertices[2]})

    assert path == edges[:1]
