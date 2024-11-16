import datetime

from src.core.engine.movements.world.criterions.item_criterion import (
    ItemCriterion,
)
from src.core.states.game_state import GameState


class MonthItemCriterion(ItemCriterion):
    def get_criterion(self, game_state: GameState) -> int:
        return datetime.datetime.now().month - 1
