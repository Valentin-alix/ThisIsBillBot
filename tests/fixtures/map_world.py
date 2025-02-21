from dofus_unity_reader.models.maps import MapReference
from dofus_unity_reader.models.world_graph import Edge, Transition, Vertice


def make_map_reference(cell_id: int | None) -> MapReference:
    return MapReference(cellId=cell_id)


def make_transition(criterion: str, transition_id: int) -> Transition:
    return Transition(
        m_type=1,
        m_direction=0,
        m_skillId=0,
        m_criterion=criterion,
        m_transitionMapId=0,
        m_cellId=0,
        m_id=transition_id,
    )


def make_edge(target_map_id: int, transition: Transition | None = None) -> Edge:
    return Edge(
        m_from=Vertice(m_mapId=1, m_zoneId=1, m_uid=1),
        m_to=Vertice(m_mapId=target_map_id, m_zoneId=1, m_uid=target_map_id),
        m_transitions=[] if transition is None else [transition],
    )
