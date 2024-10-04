from src.core.states.player_state import PlayerState
from src.core.logic.criterions.item_criterion import ItemCriterion


class SubareaItemCriterion(ItemCriterion):
    def is_respected(self, player_frame: PlayerState, *args, **kwargs) -> bool:
        player_position = PlayedCharacterManager().currentSubArea.id
        if self._operator.text in [
            ItemCriterionOperator.EQUAL,
            ItemCriterionOperator.DIFFERENT,
        ]:
            return super().is_respected
        else:
            return False

    def get_criterion(self, *args, **kwargs) -> int:
        return PlayedCharacterManager().currentSubArea.id
