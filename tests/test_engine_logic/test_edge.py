from unittest.mock import MagicMock, patch

from dofus_unity_reader.models.world_graph import Edge, Transition, Vertice

from src.core.engine.movements.world.edge import (
    _get_transition_to_valid_criterions,
    get_valid_transition,
    iter_valid_outgoing_edges,
)
from tests.setup_factory import GameStateFixture


def _make_transition(criterion: str, transition_id: int) -> Transition:
    return Transition(
        m_type=1,
        m_direction=0,
        m_skillId=0,
        m_criterion=criterion,
        m_transitionMapId=0,
        m_cellId=0,
        m_id=transition_id,
    )


def _make_edge(target_map_id: int, transition: Transition | None = None) -> Edge:
    return Edge(
        m_from=Vertice(m_mapId=1, m_zoneId=1, m_uid=1),
        m_to=Vertice(m_mapId=target_map_id, m_zoneId=1, m_uid=target_map_id),
        m_transitions=[] if transition is None else [transition],
    )


class _Criterion:
    def __init__(self, respected: bool) -> None:
        self.respected = respected

    def is_respected(self, _game_state: object) -> bool:
        return self.respected


class TestEdge(GameStateFixture):
    @patch("src.core.engine.movements.world.edge.GroupItemCriterion")
    def test_get_transition_to_valid_criterions_skips_invalid_criterions(
        self, mock_group_criterion: MagicMock
    ) -> None:
        empty_transition = _make_transition("", 1)
        invalid_transition = _make_transition("ZZ>0", 2)
        valid_transition = _make_transition("Ad>0", 3)
        criterion = MagicMock()
        mock_group_criterion.return_value = criterion

        result = _get_transition_to_valid_criterions(
            (empty_transition, invalid_transition, valid_transition),
        )

        self.assertEqual(
            result, [(empty_transition, None), (valid_transition, criterion)]
        )

    @patch("src.core.engine.movements.world.edge._get_transition_to_valid_criterions")
    def test_get_valid_transition_returns_first_respected_non_forbidden_transition(
        self, mock_get_transition_to_valid_criterions: MagicMock
    ) -> None:
        edge = _make_edge(10)
        forbidden_transition = _make_transition("", 1)
        failing_transition = _make_transition("Ad>0", 2)
        valid_transition = _make_transition("Ad>1", 3)
        mock_get_transition_to_valid_criterions.return_value = [
            (forbidden_transition, None),
            (failing_transition, _Criterion(False)),
            (valid_transition, _Criterion(True)),
        ]
        self.game_state.map.forbidden_edge_transitions = {
            (edge.m_from, edge.m_to, forbidden_transition)
        }

        result = get_valid_transition(
            edge,
            [forbidden_transition, failing_transition, valid_transition],
            self.game_state,
        )

        self.assertEqual(result, valid_transition)

    @patch("src.core.engine.movements.world.edge.edge_has_valid_transition")
    @patch("src.core.engine.movements.world.edge.MapTools.is_map_allowed_for_unsub")
    @patch("src.core.engine.movements.world.edge.WorldGraphReader")
    def test_iter_valid_outgoing_edges_filters_maps_subscriptions_and_key_errors(
        self,
        mock_world_graph_reader_class: MagicMock,
        mock_is_map_allowed_for_unsub: MagicMock,
        mock_edge_has_valid_transition: MagicMock,
    ) -> None:
        forbidden_edge = _make_edge(99)
        unsub_blocked_edge = _make_edge(100)
        invalid_edge = _make_edge(101)
        key_error_edge = _make_edge(102)
        valid_edge = _make_edge(103)

        mock_world_graph_reader = MagicMock()
        mock_world_graph_reader.get_outgoing_edges_from_vertex.return_value = [
            forbidden_edge,
            unsub_blocked_edge,
            invalid_edge,
            key_error_edge,
            valid_edge,
        ]
        mock_world_graph_reader_class.return_value = mock_world_graph_reader

        def is_map_allowed(map_id: int) -> bool:
            return map_id != 100

        def edge_has_valid_transition(edge: Edge, _game_state: object) -> bool:
            if edge.m_to.m_mapId == 101:
                return False
            if edge.m_to.m_mapId == 102:
                raise KeyError("missing criterion data")
            return True

        mock_is_map_allowed_for_unsub.side_effect = is_map_allowed
        mock_edge_has_valid_transition.side_effect = edge_has_valid_transition

        with patch("src.core.engine.movements.world.edge.Maps.FORBIDDEN", [99]):
            result = list(
                iter_valid_outgoing_edges(
                    Vertice(m_mapId=1, m_zoneId=1, m_uid=1),
                    self.game_state,
                )
            )

        self.assertEqual(result, [valid_edge])
