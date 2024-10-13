from dataclasses import dataclass

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.states.game_state import GameState


@dataclass
class QuestObjectiveItemCriterion(ItemCriterion):
    criterion: str

    def is_respected(self, game_state: GameState) -> bool:
        if not self.criterion_ref == "Qo":
            return False

        match self.item_operator.text:
            case ItemCriterionOperator.EQUAL:
                return self.criterion_value in game_state.objective.active_quest_by_id
            case ItemCriterionOperator.DIFFERENT:
                return (
                    self.criterion_value not in game_state.objective.active_quest_by_id
                )
            case ItemCriterionOperator.INFERIOR:
                return (
                    self.criterion_value
                    not in game_state.objective.finished_quest_by_id
                )
            case ItemCriterionOperator.SUPERIOR:
                return self.criterion_value in game_state.objective.finished_quest_by_id

        return False
