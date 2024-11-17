import dataclasses
from dataclasses import dataclass, field

from D3Database.models.datas.recipe_root import RecipeItem
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from src.core.engine.fights.effect import EffectActionEnum
from src.core.engine.items.item import SetPositionEnum
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
    bank_object_by_gid: dict[int, ObjectItemInventory] = dataclasses.field(
        init=False, default_factory=dict
    )
    _inventory_weight: int = dataclasses.field(init=False, default=0)
    _weight_max: int = dataclasses.field(init=False, default=1)
    objects_by_uid: ObjectByUid = field(init=False)

    def __post_init__(self):
        self.objects_by_uid = ObjectByUid()

    def clear_state(self):
        self.inventory_weight = 0
        self.weight_max = 1
        self.kamas = 0
        self.clear_inventory()

    # ==================== Inventory Operations ====================

    def set_objects(self, objects: list[ObjectItemInventory]):
        self.objects_by_uid.clear()
        for obj in objects:
            self.objects_by_uid[obj.item.uid] = obj
        self.inventory_signals.clear_inventory.emit()
        if objects:
            self.inventory_signals.added_object_items_batch.emit(objects)

    def add_object(self, obj: ObjectItemInventory):
        self.objects_by_uid[obj.item.uid] = obj
        self.inventory_signals.added_object_item.emit(obj)

    def add_objects(self, objects: list[ObjectItemInventory]):
        for obj in objects:
            self.objects_by_uid[obj.item.uid] = obj
        if objects:
            self.inventory_signals.added_object_items_batch.emit(objects)

    def remove_object(self, uid: int):
        if uid in self.objects_by_uid:
            del self.objects_by_uid[uid]
            self.inventory_signals.deleted_object_item_uid.emit(uid)

    def clear_inventory(self):
        self.objects_by_uid.clear()
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
        self.inventory_signals.inventory_weight.emit(value)

    @property
    def weight_max(self):
        return self._weight_max

    @weight_max.setter
    def weight_max(self, value: int):
        self._weight_max = value
        self.inventory_signals.weight_max.emit(value)

    @property
    def kamas(self) -> int:
        return self._kamas

    @kamas.setter
    def kamas(self, value: int):
        self._kamas = value
        self.inventory_signals.kamas.emit(value)

    def has_weapon_hunter(self):
        return any(
            object.position == SetPositionEnum.ARME
            for object in self.objects_by_uid.values()
            if any(
                effect.action == EffectActionEnum.WEAPON_HUNTER
                for effect in object.item.effects
            )
        )

    def get_valid_recipes(
        self,
        recipes: list[RecipeItem],
    ) -> list[RecipeItem]:
        """Delegate to logic layer for recipe validation."""
        from src.core.engine.crafts.recipes import get_valid_recipes

        return get_valid_recipes(self.logger, self.player_state.jobs_lvl_by_id, recipes)

    def get_object_item_by_gid(self, gid: int):
        return next(
            (obj for obj in self.objects_by_uid.values() if obj.item.gid == gid), None
        )
