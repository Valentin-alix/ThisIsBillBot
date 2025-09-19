from dataclasses import dataclass, field
from datetime import datetime, timedelta

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from inventory_pb2 import InventoryWeightEvent, ObjectSetPositionRequest

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.items.acquire_items_behavior import (
    AcquireItemsBehavior,
    ItemToAcquire,
)
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items.equipment import (
    get_best_roll,
    get_current_best_set,
    get_item_gids_to_buy,
    roll_score,
)
from src.core.engine.items.set_infos import SetOnLevel
from src.services.human_timings import HumanTimingsService


@dataclass
class AutoEquipmentBehavior(RecoverableBehavior):
    acquire_items_behavior: AcquireItemsBehavior

    _last_run_datetime: datetime | None = field(init=False, default=None)
    _chosen_set: SetOnLevel | None = field(init=False, default=None)
    _needed_gids: list[int] = field(init=False, default_factory=list[int])
    _items_to_equip: list[ObjectItemInventory] = field(init=False, default_factory=list[ObjectItemInventory])

    def run(self) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_equipping())

    def start_equipping(self):
        if self._last_run_datetime and (datetime.now() - self._last_run_datetime) < timedelta(hours=1):
            self.logger.info("Too early to start auto equipment again")
            return self.finish()

        self._last_run_datetime = datetime.now()
        self._chosen_set = None
        self._needed_gids = []
        self._items_to_equip = []

        item_infos_to_equip = self.get_item_gids_to_equip()
        if not item_infos_to_equip:
            return self.finish()

        self._needed_gids = [info.item_gid for info in item_infos_to_equip]
        items_to_acquire = [
            item_to_acquire
            for info in item_infos_to_equip
            if (item_to_acquire := self._to_acquire(info)) is not None
        ]
        if not items_to_acquire:
            return self.collect_and_equip()

        self.acquire_items_behavior.start(
            items=items_to_acquire,
            callback=self.on_items_acquired,
            parent=self,
        )

    def _to_acquire(self, info: ItemToBuyInfo) -> ItemToAcquire | None:
        primary_elem = self.game_state.fight.primary_and_second_elem[0]
        inventory_best = get_best_roll(self._copies_of(info.item_gid), primary_elem)
        if inventory_best is None:
            return ItemToAcquire(
                item_gid=info.item_gid,
                max_kamas=info.max_kamas,
                category=CategoryItemEnum.EQUIPMENT,
            )

        bank_best = get_best_roll(self._bank_copies_of(info.item_gid), primary_elem)
        if bank_best is None or roll_score(bank_best, primary_elem) <= roll_score(
            inventory_best, primary_elem
        ):
            return None

        return ItemToAcquire(
            item_gid=info.item_gid,
            max_kamas=info.max_kamas,
            category=CategoryItemEnum.EQUIPMENT,
            upgrade_from_bank=True,
        )

    def _copies_of(self, item_gid: int) -> list[ObjectItemInventory]:
        return [
            object_item
            for object_item in self.game_state.inventory.objects_by_uid.values()
            if object_item.item.gid == item_gid
        ]

    def _bank_copies_of(self, item_gid: int) -> list[ObjectItemInventory]:
        if not self.game_state.inventory.can_use_bank:
            return []
        return [
            object_item
            for object_item in self.game_state.inventory.bank_objects_by_uid.values()
            if object_item.item.gid == item_gid
        ]

    def on_items_acquired(self, error_code: str | None, missing_by_gid: dict[int, int]):
        self.raise_if_error(error_code)
        if missing_by_gid:
            self.logger.info(f"Could not source {len(missing_by_gid)} item(s); equipping what we have")
        self.collect_and_equip()

    def collect_and_equip(self):
        primary_elem = self.game_state.fight.primary_and_second_elem[0]
        self._items_to_equip = []
        for gid in self._needed_gids:
            best = get_best_roll(self._copies_of(gid), primary_elem)
            if best is not None:
                self._items_to_equip.append(best)
        self.equip_next_item()

    def get_item_gids_to_equip(self) -> list[ItemToBuyInfo]:
        set_on_level = get_current_best_set(
            self.game_state.fight.primary_and_second_elem[0],
            self.game_state.player.level,
            self.game_state.player.is_sub,
        )
        if not set_on_level:
            self.logger.info("No available set")
            return []

        self._chosen_set = set_on_level

        item_info_to_buy = get_item_gids_to_buy(set_on_level, self.game_state.inventory.objects_by_uid)
        self.logger.info(f"Gonna equip {item_info_to_buy}")

        return item_info_to_buy

    def equip_next_item(self):
        if len(self._items_to_equip) == 0:
            return self.finish()

        assert self._chosen_set

        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event_after_equipped,
            originator=self,
            once=True,
        )

        item_inventory = self._items_to_equip.pop()
        req = ObjectSetPositionRequest(
            object_uid=item_inventory.item.uid,
            quantity=1,
            position=self._chosen_set.position_by_item_id[item_inventory.item.gid],
        )
        self.send_message_delayed(
            req,
            HumanTimingsService().get_timing_equipment_choice(),
        )

    def on_inventory_weight_event_after_equipped(self, msg: InventoryWeightEvent):
        self.equip_next_item()
