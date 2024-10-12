from typing import Iterator

from models.world_graph import Edge, Vertice, Transition
from src.core.data_center.data_reader import DataReader
from src.core.data_center.world_graph_reader import WorldGraphReader
from src.core.logic.criterions.consts import CRITERION_WHITE_LIST
from src.core.logic.criterions.group_item_criterion import GroupItemCriterion
from src.core.states.game_state import GameState
from src.signals.world_signals import WorldSignals

FORBIDDEN_EDGE_TRANSITION: set[tuple[int, int, Transition]] = set()
FORBIDDEN_MAP_IDS: set[int] = {
    202899464,
    193331717,
    193331716,
    166725120,
    121766912,
    121767936,
    88082698,
    121767936,
    88083210,
    205260292,
    206047751,
    206046725,
    123470339,
}


def get_valid_transition(
    edge: Edge, transitions: list[Transition], game_state: GameState
) -> Transition | None:
    for transition in transitions:
        if (
            edge.m_from.m_uid,
            edge.m_to.m_uid,
            transition,
        ) in FORBIDDEN_EDGE_TRANSITION:
            continue

        if len(transition.m_criterion) == 0:
            return transition

        if (
            "&" not in transition.m_criterion
            and "|" not in transition.m_criterion
            and transition.m_criterion[0:2] not in CRITERION_WHITE_LIST
        ):
            continue

        criterion = GroupItemCriterion(transition.m_criterion)
        if criterion.is_respected(game_state):
            return transition
    return None


def edge_has_valid_transition(edge: Edge, game_state: GameState) -> bool:
    return (
        get_valid_transition(
            edge=edge, transitions=edge.m_transitions, game_state=game_state
        )
        is not None
    )


def iter_valid_outgoing_edges(
    vertice: Vertice, game_state: GameState
) -> Iterator[Edge]:
    edges = WorldGraphReader().get_outgoing_edges_from_vertex(vertice)
    for edge in edges:
        if edge.m_to.m_mapId in FORBIDDEN_MAP_IDS:
            continue
        if not edge_has_valid_transition(edge, game_state):
            continue
        yield edge


def draw_edge_path(world_signals: WorldSignals, edges: list[Edge]):
    world_signals.reset_path.emit()
    for edge in edges:
        start_map_pos = DataReader().map_pos_by_map_id[edge.m_from.m_mapId]
        end_map_pos = DataReader().map_pos_by_map_id[edge.m_to.m_mapId]
        world_signals.arrow_pos.emit(start_map_pos, end_map_pos)


if __name__ == "__main__":
    vertice = next(iter(WorldGraphReader().get_vertexes(217059328)))

    edges = WorldGraphReader().get_outgoing_edges_from_vertex(vertice)

    for edge in edges:
        if edge.m_to.m_mapId == 212600322:
            print(edge)
