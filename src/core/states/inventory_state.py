import dataclasses
from dataclasses import dataclass

from protos.game.common_pb2 import ObjectItemInventory
from src.core.states.state import State
from src.signals.player_signals import GameInfoSignals


@dataclass
class InventoryState(State):
    game_info_signals: GameInfoSignals
    _inventory_weight: int = dataclasses.field(init=False, default=0)
    _weight_max: int = dataclasses.field(init=False, default=1)
    _kamas: int = dataclasses.field(init=False, default=0)
    objects_by_uid: dict[int, ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=dict
    )

    def clear_state(self):
        self.inventory_weight = 0
        self.weight_max = 1
        self.kamas = 0
        self.objects_by_uid.clear()

    @property
    def pod_percentage(self):
        return self.inventory_weight / self.weight_max

    @property
    def is_full_pods(self) -> bool:
        return self.pod_percentage >= 0.95

    @property
    def inventory_weight(self):
        return self._inventory_weight

    @inventory_weight.setter
    def inventory_weight(self, value: int):
        self._inventory_weight = value
        self.game_info_signals.inventory_weight.emit(value)

    @property
    def weight_max(self):
        return self._weight_max

    @weight_max.setter
    def weight_max(self, value: int):
        self._weight_max = value
        self.game_info_signals.weight_max.emit(value)

    @property
    def kamas(self):
        return self._kamas

    @kamas.setter
    def kamas(self, value: int):
        self._kamas = value
        self.game_info_signals.kamas.emit(value)
