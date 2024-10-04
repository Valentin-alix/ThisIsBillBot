from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class StateCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        states: list = FightersStateManager().getStates(
            CurrentPlayedFighterManager().currentFighterId
        )
        if self.item_operator.text == ItemCriterionOperator.EQUAL:
            return self.criterion_value in states
        if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            return self.criterion_value not in states
        else:
            return False
