from src.core.logic.criterions.consts import CRITERION_WHITE_LIST
from src.core.logic.criterions.group_item_criterion import GroupItemCriterion
from src.core.repositories.world_graph_reader import Edge
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState

FORBIDDEN_TRANSITION_IDS: set[int] = set()


def edge_has_valid_transitions(
    edge: Edge,
    player_state: PlayerState,
    map_state: MapState,
    quest_state: ObjectiveState,
    entity_state: EntityState,
    inventory_state: InventoryState,
) -> bool:
    valid: bool = False
    for transition in edge.m_transitions.Array:
        if transition.m_id in FORBIDDEN_TRANSITION_IDS:
            continue
        valid = True
        if len(transition.m_criterion) == 0:
            continue
        if (
            "&" not in transition.m_criterion
            and "|" not in transition.m_criterion
            and transition.m_criterion[0:2] in CRITERION_WHITE_LIST
        ):
            return False
        criterion = GroupItemCriterion(transition.m_criterion)
        return criterion.is_respected(
            player_state,
            map_state=map_state,
            quest_state=quest_state,
            entity_state=entity_state,
            inventory_state=inventory_state,
        )
    return valid
