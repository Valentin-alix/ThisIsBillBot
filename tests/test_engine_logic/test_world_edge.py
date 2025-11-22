from datetime import datetime

import pytest

from DBDofusUnity.dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from DBDofusUnity.dofus_unity_reader.game_constants.map_id import FORBIDDEN_MAP_IDS
from DBDofusUnity.dofus_unity_reader.models.world_graph import Edge, Transition, Vertice

from src.core.engine.contexts import CriterionContext, WorldTransitionContext
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
    """193331717 trapped a bot in a two-map pocket after being routed into once; see test_farm_recovery.py."""
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
