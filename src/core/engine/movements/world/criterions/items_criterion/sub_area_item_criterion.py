from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)
from src.core.states.game_state import GameState


class SubareaItemCriterion(ItemCriterion):
    def is_respected(self, game_state: GameState) -> bool:
        if self.item_operator.text in [
            ItemCriterionOperator.EQUAL,
            ItemCriterionOperator.DIFFERENT,
        ]:
            return super().is_respected(game_state)
        else:
            return False

    def get_criterion(self, game_state: GameState) -> int:
        return game_state.map.sub_area_id
