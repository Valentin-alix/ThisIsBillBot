from dataclasses import dataclass, field
from datetime import datetime, timedelta
from functools import cached_property

from common_pb2 import ObjectItemInventory
from dofus_unity_reader.game_constants.item import CategoryItemEnum, ItemEnum
from inventory_pb2 import InventoryWeightEvent, ObjectSetPositionRequest
from pydantic import BaseModel

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.sale_hotel.sale_hotel_buy_behavior import (
    ItemToBuyInfo,
    SaleHotelBuyBehavior,
)
from src.core.config import BASE_RANGE
from dofus_unity_reader.game_constants.inventory_position import (
    CharacterInventoryPositionEnum,
)

type ItemByPosition = dict[CharacterInventoryPositionEnum, ItemToBuyInfo]
type PositionByItemId = dict[int, CharacterInventoryPositionEnum]


class SetOnLevel(BaseModel):
    min_level: int
    item_info_by_position: ItemByPosition

    @cached_property
    def position_by_item_id(self) -> PositionByItemId:
        return {
            value.item_gid: key for key, value in self.item_info_by_position.items()
        }


SET_BY_LEVEL_THRESHOLD: list[SetOnLevel] = [
    SetOnLevel(
        min_level=12,
        item_info_by_position={
            CharacterInventoryPositionEnum.AccessoryPositionHat: ItemToBuyInfo(
                item_gid=ItemEnum.CHAPEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionCape: ItemToBuyInfo(
                item_gid=ItemEnum.CAPE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionAmulet: ItemToBuyInfo(
                item_gid=ItemEnum.AMU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.InventoryPositionRingLeft: ItemToBuyInfo(
                item_gid=ItemEnum.ANNEAU_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBelt: ItemToBuyInfo(
                item_gid=ItemEnum.CEINTURE_PIOU_BLEU, max_kamas=2_000
            ),
            CharacterInventoryPositionEnum.AccessoryPositionBoots: ItemToBuyInfo(
                item_gid=ItemEnum.SANDALE_PIOU_BLEU, max_kamas=2_000
            ),
        },
    )
]


@dataclass
class AutoEquipmentBehavior(Behavior):
    """Check si on devrait aller acheter tel item pour les equiper puis go le buy et l'équiper si cest le cas"""

    sale_hotel_buy_behavior: SaleHotelBuyBehavior

    _last_run_datetime: datetime | None = field(init=False, default=None)
    _chosen_set: SetOnLevel | None = field(init=False, default=None)
    _bought_item: list[ObjectItemInventory] = field(
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
        self._bought_item.clear()

        item_infos_to_buy = self.get_item_gids_to_buy()
        if not item_infos_to_buy:
            return self.finish()

        self.sale_hotel_buy_behavior.start(
            callback=self.on_sale_hotel_buy_behavior_finished,
            parent=self,
            item_infos_to_buy=item_infos_to_buy,
            category=CategoryItemEnum.EQUIPMENT,
        )

    def get_item_gids_to_buy(self) -> list[ItemToBuyInfo]:
        available_set = [
            set_on_level
            for set_on_level in SET_BY_LEVEL_THRESHOLD
            if set_on_level.min_level <= self.game_state.player.level
            and (set_on_level.min_level <= 60 or self.game_state.player.is_sub)
        ]
        if not available_set:
            self.logger.info("No available set")
            return []

        best_available_set = max(
            available_set, key=lambda set_on_level: set_on_level.min_level
        )
        self._chosen_set = best_available_set

        item_info_to_buy: list[ItemToBuyInfo] = []
        for position, item_info in best_available_set.item_info_by_position.items():
            equipped_item = self.game_state.inventory.get_equipment_on_position(
                position
            )
            if not equipped_item or equipped_item.item.gid != item_info.item_gid:
                item_info_to_buy.append(item_info)

        self.logger.info(f"Gonna buy {item_info_to_buy}")

        return item_info_to_buy

    def on_sale_hotel_buy_behavior_finished(
        self, error_code: str | None, bought_item: list[ObjectItemInventory]
    ):
        self.raise_if_error(error_code)
        self._bought_item = bought_item
        self.equip_next_item()

    def equip_next_item(self):
        if len(self._bought_item) == 0:
            return self.finish()

        assert self._chosen_set

        self.event_manager.on(
            InventoryWeightEvent,
            callback=self.on_inventory_weight_event_after_equipped,
            originator=self,
            once=True,
        )

        item_inventory = self._bought_item.pop()
        req = ObjectSetPositionRequest(
            object_uid=item_inventory.item.uid,
            quantity=1,
            position=self._chosen_set.position_by_item_id[item_inventory.item.gid],
        )
        self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))

    def on_inventory_weight_event_after_equipped(self, msg: InventoryWeightEvent):
        self.equip_next_item()
