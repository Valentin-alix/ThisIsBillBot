from src.core.logic.criterions.item_criterion import ItemCriterion


class GiftItemCriterion(ItemCriterion):

    _ali_gift_id: int

    _ali_gift_level: int = -1

    def __init__(self, p_criterion: str):
        super().__init__(p_criterion)
        arrayParams: list = str(self._criterionValueText).split(",")
        if arrayParams and len(arrayParams) > 0:
            if len(arrayParams) <= 2:
                self._ali_gift_id = int(arrayParams[0])
                self._ali_gift_level = int(arrayParams[1])
        else:
            self._ali_gift_id = int(self._criterionValue)
            self._ali_gift_level = -1

    def is_respected(self, *args, **kwargs) -> bool:
        rg_i: int = 0
        rank: int = Kernel().worker.getFrameByName("AlignmentFrame")
        rankGift: AlignmentRankJntGift = (
            AlignmentRankJntGift.getAlignmentRankJntGiftById(rank)
        )
        if rankGift and rankGift.gifts:
            for rg_i in range(len(rankGift.gifts)):
                if rankGift.gifts[rg_i] == self._ali_gift_id:
                    if self._ali_gift_level != 0:
                        if rankGift.levels[rg_i] > self._ali_gift_level:
                            return True
                        return False
                    return True
        return False
