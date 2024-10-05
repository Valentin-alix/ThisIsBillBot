from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


class AchievementItemCriterion(ItemCriterion):
    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        objective_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        return self.criterion_value in objective_state.finished_achievement_by_id

    def get_criterion(
        self,
        player_state: PlayerState,
        map_state: MapState,
        objective_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> int:
        if self.criterion_value in objective_state.finished_achievement_by_id:
            return 1
        return 0
