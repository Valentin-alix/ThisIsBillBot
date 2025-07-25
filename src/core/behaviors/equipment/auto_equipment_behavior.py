from dataclasses import dataclass, field
from datetime import datetime, timedelta

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from inventory_pb2 import InventoryWeightEvent, ObjectSetPositionRequest

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.sale_hotel_buy_behavior import (
    SaleHotelBuyBehavior,
)
from src.core.behaviors.storage.loads.load_from_bank_behavior import (
    LoadFromBankBehavior,
)
from src.core.behaviors.storage.loads.load_item_request import LoadItemInfo
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
class AutoEquipmentBehavior(Behavior):
    """Equip the best set, sourcing items by priority: inventory, bank, sale hotel."""

    sale_hotel_buy_behavior: SaleHotelBuyBehavior
    load_from_bank_behavior: LoadFromBankBehavior

    _last_run_datetime: datetime | None = field(init=False, default=None)
    _chosen_set: SetOnLevel | None = field(init=False, default=None)
    _needed_gids: list[int] = field(init=False, default_factory=list[int])
    _to_buy: list[ItemToBuyInfo] = field(init=False, default_factory=list[ItemToBuyInfo])
    _items_to_equip: list[ObjectItemInventory] = field(init=False, default_factory=list[ObjectItemInventory])

    def run(self):
        if self._last_run_datetime and (datetime.now() - self._last_run_datetime) < timedelta(hours=1):
            self.logger.info("Too early to start auto equipment again")
            return self.finish()

        self._last_run_datetime = datetime.now()
        self._chosen_set = None
        self._needed_gids = []
        self._to_buy = []
        self._items_to_equip = []

        item_infos_to_equip = self.get_item_gids_to_equip()
        if not item_infos_to_equip:
            return self.finish()

        self._needed_gids = [info.item_gid for info in item_infos_to_equip]
        inventory = self.game_state.inventory
        can_bank = self.game_state.inventory.can_use_bank
        primary_elem = self.game_state.fight.primary_and_second_elem[0]

        load_from_bank: list[LoadItemInfo] = []
        self._to_buy = []
        for info in item_infos_to_equip:
            gid = info.item_gid
            inv_best = get_best_roll(
                (
                    object_item
                    for object_item in inventory.objects_by_uid.values()
                    if object_item.item.gid == gid
                ),
                primary_elem,
            )
            bank_items = (
                [
                    object_item
                    for object_item in inventory.bank_objects_by_uid.values()
                    if object_item.item.gid == gid
                ]
                if can_bank
                else []
            )
            bank_best = get_best_roll(bank_items, primary_elem)

            if bank_best is not None and (
                inv_best is None or roll_score(bank_best, primary_elem) > roll_score(inv_best, primary_elem)
            ):
                load_from_bank.append(LoadItemInfo(item_gid=gid, remaining_quantity=len(bank_items), tab=0))
            elif inv_best is None:
                self._to_buy.append(info)

        if load_from_bank:
            return self.load_from_bank_behavior.start(
                load_items_infos=load_from_bank,
                callback=self.on_bank_loaded,
                parent=self,
            )
        self.buy_missing_items()

    def on_bank_loaded(self, error_code: str | None):
        self.raise_if_error(error_code)
        self.buy_missing_items()

    def buy_missing_items(self):
        if self._to_buy and not (self.game_state.player.is_sub or self.game_state.player.is_former_sub):
            self.logger.info(
                "Sale hotel unavailable for accounts that have never subscribed; skipping equipment purchases"
            )
            self._to_buy = []
        if self._to_buy and self.game_state.inventory.is_full_pods:
            self.logger.info("Full pods: skipping sale-hotel purchase")
            self._to_buy = []
        if not self._to_buy:
            return self.collect_and_equip()

        self.sale_hotel_buy_behavior.start(
            callback=self.on_sale_hotel_buy_behavior_finished,
            parent=self,
            item_infos_to_buy=self._to_buy,
            category=CategoryItemEnum.EQUIPMENT,
        )

    def on_sale_hotel_buy_behavior_finished(
        self, error_code: str | None, bought_item: list[ObjectItemInventory]
    ):
        self.raise_if_error(error_code)
        self.collect_and_equip()

    def collect_and_equip(self):
        inventory = self.game_state.inventory
        primary_elem = self.game_state.fight.primary_and_second_elem[0]
        self._items_to_equip = []
        for gid in self._needed_gids:
            best = get_best_roll(
                (
                    object_item
                    for object_item in inventory.objects_by_uid.values()
                    if object_item.item.gid == gid
                ),
                primary_elem,
            )
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
