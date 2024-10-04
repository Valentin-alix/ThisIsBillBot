from dataclasses import dataclass

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.states.player_state import PlayerState


@dataclass
class QuestObjectiveItemCriterion(ItemCriterion):
    criterion: str

    def is_respected(self, player_state: PlayerState, *args, **kwargs) -> bool:
        if not self.criterion_ref == "Qo":
            return False

        match self.item_operator:
            case ItemCriterionOperator.EQUAL:
                return self.criterion_value in player_state.active_quest_by_id
            case ItemCriterionOperator.DIFFERENT:
                return self.criterion_value in player_state.active_quest_by_id
            case ItemCriterionOperator.INFERIOR:
                return self.criterion_value in player_state.finished_quest_by_id
            case ItemCriterionOperator.SUPERIOR:
                return self.criterion_value in player_state.finished_quest_by_id

        return False


if __name__ == "__main__":
    temp = QuestObjectiveItemCriterion(criterion="Qo>12050")
    print(temp.is_respected)
