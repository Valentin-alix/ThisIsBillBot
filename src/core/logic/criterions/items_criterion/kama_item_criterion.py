from src.core.logic.criterions.item_criterion import ItemCriterion


class KamaItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        return self.item_operator.compare(
            PlayedCharacterManager().characteristics.kamas, self.criterion_value
        )
