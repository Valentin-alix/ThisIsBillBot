from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


class StaticCriterionItemCriterion(ItemCriterion):

    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        return True
