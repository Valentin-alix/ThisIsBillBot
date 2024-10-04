from src.core.logic.criterions.item_criterion import ItemCriterion


class SpellItemCriterion(ItemCriterion):

    _spell_id: int

    def __init__(self, p_criterion: str):
        super().__init__(p_criterion)
        arrayParams: list = str(self._criterionValueText).split(",")
        if arrayParams and len(arrayParams) > 0:
            if len(arrayParams) <= 1:
                self._spell_id = int(arrayParams[0])
        else:
            self._spell_id = int(self._criterionValue)

    def is_respected(self, *args, **kwargs) -> bool:
        sp: spell_wrapper = None
        for sp in PlayedCharacterManager().playerSpellList:
            if sp.id == self._spell_id:
                if self._operator.text == ItemCriterionOperator.EQUAL:
                    return True
                return False
        if self._operator.text == ItemCriterionOperator.DIFFERENT:
            return True
        return False
