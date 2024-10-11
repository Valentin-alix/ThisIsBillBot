from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.game_state import GameState


class MapCharactersItemCriterion(ItemCriterion):
    def get_criterion(self, game_state: GameState) -> int:
        nb_characters: int = 0
        for actor_id in game_state.entity.actor_by_id.keys():
            if actor_id > 0:
                nb_characters += 1
        return nb_characters
