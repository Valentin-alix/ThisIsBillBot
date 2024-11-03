import dataclasses
from dataclasses import dataclass

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory

from src.core.states.state import State
from src.interfaces.enums.effect_action_enum import EffectActionEnum
from src.interfaces.enums.set_position_enum import SetPositionEnum
from src.signals.player_signals import GameInfoSignals


class ObjectByUid(dict[int, ObjectItemInventory]):
    def __init__(self, game_info_signals: GameInfoSignals):
        self.game_info_signals = game_info_signals
        super().__init__()
        self.game_info_signals.count_object_by_uid.emit(len(self))

    def __setitem__(self, key: int, value: ObjectItemInventory):
        res = super().__setitem__(key, value)
        self.game_info_signals.count_object_by_uid.emit(len(self))
        return res

    def __delitem__(self, key: int) -> None:
        super().__delitem__(key)
        self.game_info_signals.count_object_by_uid.emit(len(self))

    def clear(self) -> None:
        super().clear()
        self.game_info_signals.count_object_by_uid.emit(len(self))


@dataclass
class InventoryState(State):
    game_info_signals: GameInfoSignals
    kamas: int = dataclasses.field(init=False, default=500_000)
    bank_object_by_gid: dict[int, ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=dict
    )
    _inventory_weight: int = dataclasses.field(init=False, default=0)
    _weight_max: int = dataclasses.field(init=False, default=1)

    def __post_init__(self):
        self.objects_by_uid = ObjectByUid(self.game_info_signals)

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
        return self.pod_percentage >= 0.9

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

    def has_weapon_hunter(self):
        any(
            object.position == SetPositionEnum.ARME
            for object in self.objects_by_uid.values()
            if any(
                effect.action == EffectActionEnum.WEAPON_HUNTER
                for effect in object.item.effects
            )
        )
