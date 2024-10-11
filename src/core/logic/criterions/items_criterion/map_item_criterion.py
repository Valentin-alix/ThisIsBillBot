from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class MapItemCriterion(ItemCriterion):
    def get_criterion(self, game_state: GameState) -> int:
        return game_state.map.map_id
