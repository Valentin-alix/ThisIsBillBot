from src.core.logic.criterions.item_criterion import ItemCriterion
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState


class MapCharactersItemCriterion(ItemCriterion):
    def get_criterion(
        self, player_frame: PlayerState, entity_state: EntityState
    ) -> int:
        nb_characters: int = 0
        for actor_info in entity_state.entities_actors_by_id.values():
            if actor_info.entity.actor_id > 0:
                nb_characters += 1
        return nb_characters
