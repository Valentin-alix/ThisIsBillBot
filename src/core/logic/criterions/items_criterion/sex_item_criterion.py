from src.core.logic.criterions.item_criterion import ItemCriterion


class SexItemCriterion(ItemCriterion):

    def get_criterion(self, *args, **kwargs) -> int:
        return int(PlayedCharacterManager().infos.sex)
