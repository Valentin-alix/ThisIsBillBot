from collections import defaultdict
from dataclasses import dataclass, field
from functools import partial

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from pydantic import BaseModel

from src.core.behaviors.recovery import RecoverableBehavior
from src.core.behaviors.sale_hotel.sale_hotel_buy_behavior import SaleHotelBuyBehavior
from src.core.behaviors.storage.loads.load_from_bank_behavior import (
    LoadFromBankBehavior,
)
from src.core.behaviors.storage.loads.load_item_request import (
    LoadItemInfo,
    get_owned_quantity,
)
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items.item_formatter import format_item_name


class ItemToAcquire(BaseModel):
    item_gid: int
    quantity: int = 1
    max_kamas: int
    category: CategoryItemEnum = CategoryItemEnum.RESOURCES
    upgrade_from_bank: bool = False


@dataclass
class AcquireItemsBehavior(RecoverableBehavior):
    load_from_bank_behavior: LoadFromBankBehavior
    sale_hotel_buy_behavior: SaleHotelBuyBehavior

    _requests_by_gid: dict[int, ItemToAcquire] = field(init=False, default_factory=dict[int, ItemToAcquire])
    _pending_categories: list[CategoryItemEnum] = field(init=False, default_factory=list[CategoryItemEnum])

    def run(self, items: list[ItemToAcquire]) -> None:
        self.init_recovery_listeners()
        self.ensure_free_to_act(lambda: self.start_acquiring(items=items))

    def start_acquiring(self, items: list[ItemToAcquire]) -> None:
        self._requests_by_gid = _merge_by_gid(items)
        self._pending_categories = []

        bank_load_by_gid = self._bank_load_by_gid()
        if not bank_load_by_gid and not self._missing_by_gid():
            self.logger.info("Everything is already in the inventory, nothing to acquire")
            return self.finish(missing_by_gid={})

        if not self._should_visit_bank(bank_load_by_gid):
            return self.buy_missing_items()

        self.logger.info(f"Withdrawing {self._format(bank_load_by_gid)} from the bank")
        self.load_from_bank_behavior.start(
            load_items_infos=[
                LoadItemInfo(item_gid=item_gid, remaining_quantity=quantity, tab=0)
                for item_gid, quantity in bank_load_by_gid.items()
            ],
            unload_first=False,
            callback=self.on_load_from_bank_behavior_finished,
            parent=self,
        )

    def on_load_from_bank_behavior_finished(
        self, error_code: str | None, load_items_infos: list[LoadItemInfo]
    ) -> None:
        del load_items_infos
        if error_code is not None:
            self.logger.info(f"Bank leg gave up ({error_code}), falling back to the sale hotel")
        self.buy_missing_items()

    def buy_missing_items(self) -> None:
        missing_by_gid = self._missing_by_gid()
        if not missing_by_gid:
            self.logger.info("The bank covered everything, no purchase needed")
            return self.finish(missing_by_gid={})

        if not (self.game_state.player.is_sub or self.game_state.player.is_former_sub):
            self.logger.info(
                "Sale hotel unavailable for accounts that have never subscribed; skipping purchases"
            )
            return self.finish(missing_by_gid=missing_by_gid)
        if self.game_state.inventory.is_full_pods:
            self.logger.info("Full pods: skipping sale-hotel purchase")
            return self.finish(missing_by_gid=missing_by_gid)

        self._pending_categories = sorted(
            {self._requests_by_gid[item_gid].category for item_gid in missing_by_gid}
        )
        self.logger.info(f"Buying {self._format(missing_by_gid)} at the sale hotel")
        self.buy_next_category()

    def buy_next_category(self) -> None:
        if not self._pending_categories:
            return self.finish(missing_by_gid=self._missing_by_gid())

        category = self._pending_categories.pop(0)
        item_infos_to_buy = [
            ItemToBuyInfo(item_gid=item_gid, max_kamas=self._requests_by_gid[item_gid].max_kamas)
            for item_gid, quantity in self._missing_by_gid().items()
            if self._requests_by_gid[item_gid].category == category
            for _ in range(quantity)
        ]
        if not item_infos_to_buy:
            return self.buy_next_category()

        self.sale_hotel_buy_behavior.start(
            item_infos_to_buy=item_infos_to_buy,
            category=category,
            callback=partial(self.on_sale_hotel_buy_behavior_finished, category=category),
            parent=self,
        )

    def on_sale_hotel_buy_behavior_finished(
        self,
        error_code: str | None,
        bought_item: list[ObjectItemInventory],
        category: CategoryItemEnum,
    ) -> None:
        if error_code is not None:
            self.logger.warning(f"Sale hotel gave up on category {category}: {error_code}")
            return self.finish(error_code, missing_by_gid=self._missing_by_gid())

        self.logger.info(f"Bought {len(bought_item)} item(s) in category {category}")
        self.buy_next_category()

    def _missing_by_gid(self) -> dict[int, int]:
        missing_by_gid: dict[int, int] = {}
        for item_gid, request in self._requests_by_gid.items():
            missing = request.quantity - get_owned_quantity(self.game_state, item_gid)
            if missing > 0:
                missing_by_gid[item_gid] = missing
        return missing_by_gid

    def _bank_load_by_gid(self) -> dict[int, int]:
        missing_by_gid = self._missing_by_gid()
        bank_load_by_gid: dict[int, int] = {}
        for item_gid, request in self._requests_by_gid.items():
            quantity = missing_by_gid.get(item_gid, 0)
            if quantity == 0 and request.upgrade_from_bank:
                quantity = 1
            if quantity > 0:
                bank_load_by_gid[item_gid] = quantity
        return bank_load_by_gid

    def _should_visit_bank(self, bank_load_by_gid: dict[int, int]) -> bool:
        inventory = self.game_state.inventory
        if not bank_load_by_gid or not inventory.can_use_bank:
            return False
        if not inventory.bank_content_known:
            return True
        return any(inventory.get_bank_object_by_gid(item_gid) is not None for item_gid in bank_load_by_gid)

    def _format(self, missing_by_gid: dict[int, int]) -> str:
        return ", ".join(
            f"{format_item_name(item_gid)} x{quantity}" for item_gid, quantity in missing_by_gid.items()
        )


def _merge_by_gid(items: list[ItemToAcquire]) -> dict[int, ItemToAcquire]:
    quantity_by_gid: defaultdict[int, int] = defaultdict(int)
    upgrade_gids: set[int] = set()
    request_by_gid: dict[int, ItemToAcquire] = {}
    for item in items:
        quantity_by_gid[item.item_gid] += item.quantity
        if item.upgrade_from_bank:
            upgrade_gids.add(item.item_gid)
        previous = request_by_gid.get(item.item_gid)
        if previous is None or item.max_kamas > previous.max_kamas:
            request_by_gid[item.item_gid] = item
    return {
        item_gid: request.model_copy(
            update={
                "quantity": quantity_by_gid[item_gid],
                "upgrade_from_bank": item_gid in upgrade_gids,
            }
        )
        for item_gid, request in request_by_gid.items()
    }
