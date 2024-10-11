from datetime import datetime

from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class DayItemCriterion(ItemCriterion):
    def get_criterion(self, game_state: GameState) -> int:
        return datetime.now().day
