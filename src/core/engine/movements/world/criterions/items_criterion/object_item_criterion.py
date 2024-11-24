from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.engine.movements.world.criterions.item_criterion_operator import (
    ItemCriterionOperator,
)
from src.core.states.game_state import GameState


class ObjectItemCriterion(ItemCriterion):
    def __init__(self, p_criterion: str):
        self._criterion_value_quantity = -1
        super().__init__(p_criterion)
        if "," in self.criterion_value_text:
            item_id_and_quantity = self.criterion_value_text.split(",")
            self.criterion_value = int(item_id_and_quantity[0])
            self._criterion_value_quantity = int(item_id_and_quantity[1])

    def is_respected(self, game_state: GameState) -> bool:
        item_quantity: int = 0
        for _object in game_state.inventory.objects_by_uid.values():
            if _object.item.gid == self.criterion_value:
                item_quantity = _object.item.quantity
                break

        if self.item_operator.text == ItemCriterionOperator.EQUAL:
            if self._criterion_value_quantity == -1:
                return item_quantity > 0
            return item_quantity == self._criterion_value_quantity
        if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            if self._criterion_value_quantity == -1:
                return item_quantity == 0
            return item_quantity != self._criterion_value_quantity
        if self.item_operator.text == ItemCriterionOperator.SUPERIOR:
            return item_quantity > max(self._criterion_value_quantity, 0)
        if self.item_operator.text == ItemCriterionOperator.INFERIOR:
            return item_quantity < max(self._criterion_value_quantity, 1)
        return False
