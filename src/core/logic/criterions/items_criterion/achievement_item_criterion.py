from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class AchievementItemCriterion(ItemCriterion):
    def is_respected(self, game_state: GameState) -> bool:
        return self.criterion_value in game_state.objective.finished_achievement_by_id

    def get_criterion(self, game_state: GameState) -> int:
        if self.criterion_value in game_state.objective.finished_achievement_by_id:
            return 1
        return 0
