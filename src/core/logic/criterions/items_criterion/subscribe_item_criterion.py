from datetime import datetime

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


class SubscribeItemCriterion(ItemCriterion):

    def get_criterion(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> int:
        if datetime.now() < player_state.subscription_end_date:
            return 1
        return 0
