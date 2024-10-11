from abc import ABC, abstractmethod

from src.core.states.game_state import GameState


class IItemCriterion(ABC):
    @abstractmethod
    def is_respected(self, game_state: GameState) -> bool: ...
