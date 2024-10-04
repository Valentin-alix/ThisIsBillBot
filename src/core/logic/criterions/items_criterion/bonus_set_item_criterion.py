from src.core.logic.criterions.item_criterion import ItemCriterion


class BonusSetItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        return self.item_operator.compare(
            int(self.get_criterion()), self.criterion_value
        )

    def get_criterion(self, *args, **kwargs) -> int:
        iw: item_wrapper = None
        bonus_per_set: int = 0
        nb_bonus: int = 0
        sets: dict = dict()
        for iw in InventoryManager().inventory.getView("equipment").content:
            if iw:
                if iw.itemSetId > 0:
                    if sets[iw.itemSetId] > 0:
                        sets[iw.itemSetId] += 1
                    if sets[iw.itemSetId] == -1:
                        sets[iw.itemSetId] = 1
                    if not sets[iw.itemSetId]:
                        sets[iw.itemSetId] = -1
        for bonus_per_set in sets:
            if bonus_per_set > 0:
                nb_bonus += bonus_per_set
        return nb_bonus
