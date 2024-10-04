from src.core.logic.criterions.item_criterion import ItemCriterion


class LevelItemCriterion(ItemCriterion):
    def get_criterion(self, *args, **kwargs) -> int:
        return PlayedCharacterManager().limitedLevel
