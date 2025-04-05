from dataclasses import dataclass, field
from datetime import datetime, timedelta

from datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum
from inventory_pb2 import InventoryWeightEvent, ObjectSetPositionRequest

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.sale_hotel_buy_behavior import (
    SaleHotelBuyBehavior,
)
from src.core.config import BASE_RANGE
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.items.equipment import (
    SetOnLevel,
    get_current_best_set,
    get_item_gids_to_buy,
)


@dataclass
class AutoEquipmentBehavior(Behavior):
    """Check si on devrait aller acheter tel item pour les equiper puis go le buy et l'équiper si cest le cas"""

    sale_hotel_buy_behavior: SaleHotelBuyBehavior

    _last_run_datetime: datetime | None = field(init=False, default=None)
    _chosen_set: SetOnLevel | None = field(init=False, default=None)
    _items_to_equip: list[ObjectItemInventory] = field(
        init=False, default_factory=list[ObjectItemInventory]
    )

    def run(self):
        if self._last_run_datetime and (
            datetime.now() - self._last_run_datetime
        ) < timedelta(hours=1):
            self.logger.info("Too early to start auto equipment again")
            return self.finish()

        self._last_run_datetime = datetime.now()
        self._chosen_set = None
        self._items_to_equip.clear()

        item_infos_to_equip = self.get_item_gids_to_equip()
        if not item_infos_to_equip:
            return self.finish()

        self.sale_hotel_buy_behavior.start(
            callback=self.on_sale_hotel_buy_behavior_finished,
            parent=self,
            item_infos_to_buy=item_infos_to_equip,
            category=CategoryItemEnum.EQUIPMENT,
        )

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

        item_info_to_buy = get_item_gids_to_buy(
            set_on_level, self.game_state.inventory.objects_by_uid
        )
        self.logger.info(f"Gonna equip {item_info_to_buy}")

        return item_info_to_buy

    def on_sale_hotel_buy_behavior_finished(
        self, error_code: str | None, bought_item: list[ObjectItemInventory]
    ):
        self.raise_if_error(error_code)
        self._items_to_equip = bought_item
        self.equip_next_item()

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
        self.send_message_delayed(req, BASE_RANGE)

    def on_inventory_weight_event_after_equipped(self, msg: InventoryWeightEvent):
        self.equip_next_item()
