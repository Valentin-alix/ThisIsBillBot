from dataclasses import dataclass

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.states.entity_state import EntityState
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.objective_state import ObjectiveState
from src.core.states.player_state import PlayerState


@dataclass
class QuestObjectiveItemCriterion(ItemCriterion):
    criterion: str

    def is_respected(
        self,
        player_state: PlayerState,
        map_state: MapState,
        quest_state: ObjectiveState,
        entity_state: EntityState,
        inventory_state: InventoryState,
    ) -> bool:
        if not self.criterion_ref == "Qo":
            return False

        match self.item_operator:
            case ItemCriterionOperator.EQUAL:
                return self.criterion_value in quest_state.active_quest_by_id
            case ItemCriterionOperator.DIFFERENT:
                return self.criterion_value in quest_state.active_quest_by_id
            case ItemCriterionOperator.INFERIOR:
                return self.criterion_value in quest_state.finished_quest_by_id
            case ItemCriterionOperator.SUPERIOR:
                return self.criterion_value in quest_state.finished_quest_by_id

        return False


if __name__ == "__main__":
    temp = QuestObjectiveItemCriterion(criterion="Qo>12050")
    print(temp.is_respected)
