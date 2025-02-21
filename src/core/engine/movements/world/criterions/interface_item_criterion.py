from abc import ABC, abstractmethod

from src.core.engine.contexts import CriterionContext


class IItemCriterion(ABC):
    @abstractmethod
    def is_respected(self, context: CriterionContext) -> bool: ...
