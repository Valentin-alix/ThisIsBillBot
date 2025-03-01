from typing import Iterator

from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.world_graph_reader import WorldGraphReader
from dofus_unity_reader.game_constants.map_id import FORBIDDEN_MAP_IDS
from dofus_unity_reader.models.datas.map_positions_root import MapPositionsRootItem
from dofus_unity_reader.models.world_graph import Edge, Transition, Vertice
from python_utils.cache import cache

from src.core.engine.contexts import WorldTransitionContext
from src.core.engine.movements.map.map_tools import MapTools
from dofus_unity_reader.game_constants.transition_type import CRITERION_WHITE_LIST
from src.core.engine.movements.world.criterions.group_item_criterion import (
    GroupItemCriterion,
)
from src.core.engine.movements.world.criterions.interface_item_criterion import (
    IItemCriterion,
)
from src.core.signals.world_signals import WorldSignals


def remove_forbidden_edge_transition_by_map_id(
    map_id: int,
    forbidden_edge_transitions: set[tuple[Vertice, Vertice, Transition]],
) -> None:
    for (
        vertice_from,
        vertice_to,
        transition,
    ) in forbidden_edge_transitions.copy():
        if vertice_from.m_mapId == map_id:
            forbidden_edge_transitions.remove((vertice_from, vertice_to, transition))


def get_valid_transition(
    edge: Edge, transitions: list[Transition], context: WorldTransitionContext
) -> Transition | None:
    for transition, criterion in _get_transition_to_valid_criterions(
        tuple(transitions)
    ):
        if (
            edge.m_from,
            edge.m_to,
            transition,
        ) in context.forbidden_edge_transitions:
            continue
        if not criterion or criterion.is_respected(context.criterion):
            return transition
    return None


@cache
def _get_transition_to_valid_criterions(
    transitions: tuple[Transition],
) -> list[tuple[Transition, IItemCriterion | None]]:
    transitions_with_criterion: list[tuple[Transition, IItemCriterion | None]] = []
    for transition in transitions:
        if len(transition.m_criterion) == 0:
            transitions_with_criterion.append((transition, None))
        if (
            "&" not in transition.m_criterion
            and "|" not in transition.m_criterion
            and transition.m_criterion[0:2] not in CRITERION_WHITE_LIST
        ):
            continue
        transitions_with_criterion.append(
            (transition, GroupItemCriterion(transition.m_criterion))
        )
    return transitions_with_criterion


def edge_has_valid_transition(edge: Edge, context: WorldTransitionContext) -> bool:
    return (
        get_valid_transition(edge=edge, transitions=edge.m_transitions, context=context)
        is not None
    )


def iter_valid_outgoing_edges(
    vertice: Vertice, context: WorldTransitionContext
) -> Iterator[Edge]:
    edges = WorldGraphReader().get_outgoing_edges_from_vertex(vertice)
    for edge in edges:
        if edge.m_to.m_mapId in FORBIDDEN_MAP_IDS:
            continue
        try:
            if not context.criterion.is_sub and not MapTools.is_map_allowed_for_unsub(
                edge.m_to.m_mapId
            ):
                continue
            if not edge_has_valid_transition(edge, context):
                continue
        except KeyError:
            continue
        yield edge


def draw_edge_path(world_signals: WorldSignals, edges: list[Edge]) -> None:
    world_signals.reset_path.emit()
    batch: list[tuple[MapPositionsRootItem, MapPositionsRootItem]] = []
    for edge in edges:
        start_map_pos = DataReader().map_pos_by_map_id[edge.m_from.m_mapId]
        end_map_pos = DataReader().map_pos_by_map_id[edge.m_to.m_mapId]
        batch.append((start_map_pos, end_map_pos))
    if batch:
        world_signals.arrow_pos_batch.emit(batch)


# Passage vers berceau d'alma, donc peux pas
# Forbidden edge : Edge(m_from=Vertice(m_mapId=54162757, m_zoneId=1, m_uid=1795), m_to=Vertice(m_mapId=57016832, m_zoneId=1, m_uid=6791), m_transitions=[Transition(m_type=3
# 2, m_direction=255, m_skillId=184, m_criterion='', m_transitionMapId=57016832, m_cellId=132, m_id=456644)]) with transition : Transition(m_type=32, m_direction=255, m_ski
# llId=184, m_criterion='', m_transitionMapId=57016832, m_cellId=132, m_id=456644)
