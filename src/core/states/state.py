from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.signals.player_signals import StatePropertySignals


@dataclass
class State(ABC):
    state_property_signals: StatePropertySignals

    def __setattr__(self, key: str, value: Any):
        if "state_property_signals" in self.__dict__:
            if isinstance(value, (int, float, str, bool, datetime)):
                if isinstance(value, datetime):
                    readable_value = value.isoformat()
                else:
                    readable_value = str(value)
                self.state_property_signals.property_set_by_class.emit(
                    self.__class__.__name__, key, readable_value
                )
        return super().__setattr__(key, value)
