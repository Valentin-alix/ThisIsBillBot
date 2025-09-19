import dataclasses
from dataclasses import dataclass, field

from datas.protos.non_obf.game.common_pb2 import (
    ObjectItemInventory,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.game_constants.effect_action import EffectActionEnum
from dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)

from src import const
from src.core.signals.player_signals import InventorySignals
from src.core.states.player_state import PlayerState
from src.core.states.state import State


class ObjectByUid(dict[int, ObjectItemInventory]):
    pass


@dataclass
class InventoryState(State):
    inventory_signals: InventorySignals
    player_state: PlayerState
    _kamas: int = dataclasses.field(init=False, default=500_000)
    _inventory_weight: int = dataclasses.field(init=False, default=0)
    _weight_max: int = dataclasses.field(init=False, default=1)
    bank_objects_by_uid: dict[int, ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=dict[int, ObjectItemInventory]
    )
    bank_content_known: bool = dataclasses.field(init=False, default=False)
    objects_by_uid: ObjectByUid = field(init=False, default_factory=ObjectByUid)

    def get_unlinked_objects(self) -> list[ObjectItemInventory]:
        return [
            object
            for object in self.objects_by_uid.values()
            if object.position == CharacterInventoryPositionEnum.InventoryPositionNotEquiped.value
            and all(effect.action != EffectActionEnum.LINKED_TO_CHARACTER for effect in object.item.effects)
            and not DataReader().item_by_id[object.item.gid].realWeight == 0
        ]

    def get_bank_objects_by_gid(self) -> dict[int, ObjectItemInventory]:
        objects_by_gid: dict[int, ObjectItemInventory] = {}
        for object_item in self.bank_objects_by_uid.values():
            gid = object_item.item.gid
            if gid not in objects_by_gid:
                objects_by_gid[gid] = object_item
            else:
                objects_by_gid[gid].item.quantity += object_item.item.quantity
        return objects_by_gid

    def get_bank_object_by_gid(self, gid: int) -> ObjectItemInventory | None:
        return next(
            (object_item for object_item in self.bank_objects_by_uid.values() if object_item.item.gid == gid),
            None,
        )

    # ==================== Inventory Operations ====================

    def set_objects(self, objects: list[ObjectItemInventory]):
        self.objects_by_uid.clear()
        for obj in objects:
            self.objects_by_uid[obj.item.uid] = obj
        if const.DEBUG:
            self.inventory_signals.clear_inventory.emit()
            if objects:
                self.inventory_signals.added_object_items_batch.emit(objects)

    def add_object(self, obj: ObjectItemInventory):
        self.objects_by_uid[obj.item.uid] = obj
        if const.DEBUG:
            self.inventory_signals.added_object_item.emit(obj)

    def add_objects(self, objects: list[ObjectItemInventory]):
        for obj in objects:
            self.objects_by_uid[obj.item.uid] = obj
        if objects and const.DEBUG:
            self.inventory_signals.added_object_items_batch.emit(objects)

    def remove_object(self, uid: int):
        if uid in self.objects_by_uid:
            del self.objects_by_uid[uid]
            if const.DEBUG:
                self.inventory_signals.deleted_object_item_uid.emit(uid)

    def clear_inventory(self):
        self.objects_by_uid.clear()
        if const.DEBUG:
            self.inventory_signals.clear_inventory.emit()

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
        if const.DEBUG:
            self.inventory_signals.inventory_weight.emit(value)

    @property
    def weight_max(self):
        return self._weight_max

    @weight_max.setter
    def weight_max(self, value: int):
        self._weight_max = value
        if const.DEBUG:
            self.inventory_signals.weight_max.emit(value)

    @property
    def kamas(self) -> int:
        return self._kamas

    @kamas.setter
    def kamas(self, value: int):
        self._kamas = value
        if const.DEBUG:
            self.inventory_signals.kamas.emit(value)

    def get_object_item_by_gid(self, gid: int) -> ObjectItemInventory | None:
        return next((obj for obj in self.objects_by_uid.values() if obj.item.gid == gid), None)

    @property
    def can_use_bank(self) -> bool:
        return (self.player_state.is_sub or self.player_state.is_former_sub) and self.kamas > 1_000
