from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)
from src.core.states.game_state import GameState


class StateCriterion(ItemCriterion):
    def is_respected(self, game_state: GameState) -> bool:
        match self.item_operator.text:
            case ItemCriterionOperator.EQUAL:
                # return
                ...
            case ItemCriterionOperator.DIFFERENT:
                ...
            case _:
                return False
        return False
