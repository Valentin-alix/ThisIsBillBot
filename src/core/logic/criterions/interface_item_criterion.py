from abc import ABC, abstractmethod

from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState


class IItemCriterion(ABC):
    @abstractmethod
    def is_respected(self, player_state: PlayerState, entity_state: EntityState): ...
