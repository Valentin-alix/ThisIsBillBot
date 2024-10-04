from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.datas.data_enum import DataEnum


class SoulStoneItemCriterion(ItemCriterion):

    ID_SOUL_STONE: list = [
        DataEnum.ITEM_GID_SOULSTONE,
        DataEnum.ITEM_GID_SOULSTONE_MINIBOSS,
        DataEnum.ITEM_GID_SOULSTONE_BOSS,
    ]

    _quantity_monster: int = 1

    _monster_id: int

    _monster_name: str

    def __init__(self, p_criterion: str):
        super().__init__(p_criterion)
        arrayParams: list = str(self.criterion_value_text).split(",")
        if arrayParams and len(arrayParams) > 0:
            if len(arrayParams) <= 2:
                self._monster_id = int(arrayParams[0])
                self._quantity_monster = int(arrayParams[1])
        else:
            self._monster_id = int(self.criterion_value)
        self._monster_name = Monster.getMonsterById(self._monster_id).name

    def is_respected(self, *args, **kwargs) -> bool:
        iw: ItemWrapper = None
        soul_stone_id: int = 0
        for iw in InventoryManager().realInventory:
            for soul_stone_id in self.ID_SOUL_STONE:
                if iw.objectGID == soul_stone_id:
                    return True
        return False
