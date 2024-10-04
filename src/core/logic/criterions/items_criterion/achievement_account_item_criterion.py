from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.logic.criterions.item_criterion_operator import ItemCriterionOperator
from src.core.states.player_state import PlayerState


class AchievementAccountItemCriterion(ItemCriterion):
    def is_respected(self, player_frame: PlayerState, *args, **kwargs) -> bool:
        server_type: int = player_frame.server.gameTypeId
        if self.item_operator.text == ItemCriterionOperator.DIFFERENT:
            if (
                self.get_criterion() == 0
                or server_type == GameServerTypeEnum.SERVER_TYPE_EPIC
            ):
                return True
            return False
        if self.get_criterion() == 1:
            return True
        return False

    def get_criterion(self, *args, **kwargs) -> int:
        achievement_finished_list = Kernel().questFrame.finishedAchievements
        character_id = PlayedCharacterManager().id
        for ach in achievement_finished_list:
            if ach.id == self.criterion_value and ach.achievedBy != character_id:
                return 1
        return 0
