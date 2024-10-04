from src.core.logic.criterions.item_criterion import ItemCriterion


class SmileyPackItemCriterion(ItemCriterion):
    def is_respected(self, *args, **kwargs) -> bool:
        pack: SmileyPack = None
        pack_list = Kernel().chatFrame
        for pack in pack_list:
            if pack.id == self._criterionValue:
                return False
        return True

    def get_criterion(self, *args, **kwargs) -> int:
        pack_list = Kernel().chatFrame.packList
        for pack in pack_list:
            if pack.id == self._criterionValue:
                return 1
        return 0
