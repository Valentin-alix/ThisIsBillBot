from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator


class ObjectItemCriterion(ItemCriterion):

    def __init__(self, p_criterion: str):
        self._criterion_value_quantity = -1
        super().__init__(p_criterion)
        if self.criterion_value == 0 and "," in self.criterion_value_text:
            item_id_and_quantity = self.criterion_value_text.split(",")
            self.criterion_value = int(item_id_and_quantity[0])
            self._criterion_value_quantity = int(item_id_and_quantity[1])
            if (
                self._criterion_value_quantity == 0
                and str(item_id_and_quantity[1]).index("0") == -1
            ):
                self._criterion_value_quantity = -1

    def is_respected(self, *args, **kwargs) -> bool:
        iw: item_wrapper = None
        item_quantity: int = 0
        for iw in InventoryManager().realInventory:
            if iw.objectGID == self.criterion_value:
                item_quantity = iw.quantity
                break
        if self.item_operator.text == ItemCriterionOperator.EQUAL:
            return (
                self._criterion_value_quantity == item_quantity > 0
                if -1
                else item_quantity == self._criterion_value_quantity
            )
        if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            return (
                self._criterion_value_quantity == item_quantity == 0
                if -1
                else item_quantity != self._criterion_value_quantity
            )
        if self.item_operator.text == ItemCriterionOperator.SUPERIOR:
            return item_quantity > max(self._criterion_value_quantity, 0)
        if self.item_operator.text == ItemCriterionOperator.INFERIOR:
            return item_quantity < max(self._criterion_value_quantity, 1)
        return False
