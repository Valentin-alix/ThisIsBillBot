from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState


class AchievementItemCriterion(ItemCriterion):
    def is_respected(self, player_frame: PlayerState, *args, **kwargs) -> bool:
        achievement_finished_list = Kernel().questFrame.finishedAccountAchievementIds
        for id in achievement_finished_list:
            if id == self.criterion_value:
                return True
        return False

    def get_criterion(
        self, player_state: PlayerState, entity_state: EntityState
    ) -> int:
        achievement_finished_list = Kernel().questFrame.finishedAccountAchievementIds
        for id in achievement_finished_list:
            if id == self.criterion_value:
                return 1
        return 0
