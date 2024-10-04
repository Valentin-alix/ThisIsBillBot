from src.core.logic.criterions.item_criterion import ItemCriterion


class ServerTypeItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        if self.item_operator.compare(
            PlayerManager().serverGameType, self.criterion_value
        ):
            return True
        return False
