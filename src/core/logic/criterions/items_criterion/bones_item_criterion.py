from src.core.logic.criterions.item_criterion import ItemCriterion


class BonesItemCriterion(ItemCriterion):

    def is_respected(self, *args, **kwargs) -> bool:
        if self.criterion_value == 0 and self.criterion_value_text == "B":
            return PlayedCharacterManager().infos.entityLook.bonesId == 1
        return PlayedCharacterManager().infos.entityLook.bonesId == self.criterion_value

    def get_criterion(self, *args, **kwargs) -> int:
        return PlayedCharacterManager().infos.entityLook.bonesId
