from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class MountFamilyItemCriterion(ItemCriterion):
    def get_criterion(self, player_frame: PlayerState, *args, **kwargs) -> int:
        mount: MountData = PlayedCharacterManager().mount
        if not mount or not PlayedCharacterManager().isRidding:
            return -1
        return mount.model.familyId
