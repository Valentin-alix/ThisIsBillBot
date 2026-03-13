from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.character_pb2 import CharacterCharacteristicUpgradeResultEvent
from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import ObjectItemInventory
from DBDofusUnity.datas.protos.non_obf.game.exchange_pb2 import ExchangeObjectMoveRequest
from DBDofusUnity.datas.protos.non_obf.game.inventory_pb2 import InventoryWeightEvent
from DBDofusUnity.dofus_unity_reader.data_center.data_reader import DataReader
from DBDofusUnity.dofus_unity_reader.game_constants.area import AreaEnum, SubAreaEnum
from DBDofusUnity.dofus_unity_reader.game_constants.item import CategoryItemEnum, ItemEnum
from DBDofusUnity.dofus_unity_reader.models.datas.recipe_root import RecipeItem
from src.controller.game_data import GameDataController
from src.core.behaviors.craft.craft_behavior import CraftBehavior, CraftRequest
from src.core.behaviors.farms.base_farm_behavior import BaseFarmingErrorCode
from src.core.behaviors.farms.fight.fighter_behavior import FighterBehavior
from src.core.behaviors.farms.harvest.harvester_behavior import HarvesterBehavior
from src.core.behaviors.items.auto_equipment_behavior import AutoEquipmentBehavior
from src.core.behaviors.quests.quest_behavior import QuestBehavior
from src.core.behaviors.recovery_behavior import RecoverableBehavior
from src.core.behaviors.sale_hotel.sale_hotel_buy_behavior import SaleHotelBuyBehavior
from src.core.behaviors.sale_hotel.sale_hotel_sell_behavior import SaleHotelSellBehavior
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestBehavior,
)
from src.core.engine.economy.sale_hotel import ItemToBuyInfo
from src.core.engine.fights.stats.characteristic import build_characteristic_upgrade_request
from src.core.engine.quests.scripts import QUEST_SCRIPTS
from src.services.human_timings import HumanTimingsService

SMOKE_TEST_RECIPE_RESULT_ID = ItemEnum.ANKARNOOB_BREAD
SMOKE_TEST_RECIPE_QUANTITY = 2
SMOKE_TEST_HARVEST_AREA_ID = AreaEnum.ASTRUB
SMOKE_TEST_HARVEST_SUB_AREA_ID = SubAreaEnum.ASTRUB_FIELD
SMOKE_TEST_BUY_MAX_KAMAS = 5000
CHARACTERISTIC_UPGRADE_POINTS = 1

BANK_ROUNDTRIP_TIMEOUT_SECONDS = 10.0
CHARACTERISTIC_UPGRADE_TIMEOUT_SECONDS = 10.0


class SmokeTestErrorCode(StrEnum):
    BANK_ROUNDTRIP_TIMEOUT = auto()
    BANK_ROUNDTRIP_INCOHERENT = auto()
    SALE_HOTEL_INCOHERENT = auto()
    CHARACTERISTIC_UPGRADE_TIMEOUT = auto()
    CHARACTERISTIC_UPGRADE_INCOHERENT = auto()


@dataclass
class SmokeTestBehavior(RecoverableBehavior):
    auto_equipment_behavior: AutoEquipmentBehavior
    fighter_behavior: FighterBehavior
    harvester_behavior: HarvesterBehavior
    craft_behavior: CraftBehavior
    enter_bank_chest_behavior: EnterBankChestBehavior
    sale_hotel_sell_behavior: SaleHotelSellBehavior
    sale_hotel_buy_behavior: SaleHotelBuyBehavior
    quest_behavior: QuestBehavior

    _smoke_test_recipe: RecipeItem | None = field(init=False, default=None)
    _bank_roundtrip_item_gid: int = field(init=False, default=0)
    _bank_roundtrip_quantity: int = field(init=False, default=0)
    _bank_roundtrip_bank_qty_before: int = field(init=False, default=0)

    def run(self) -> None:
        self.ensure_free_to_act(self.step_fighter)

    def _next(self, step: Callable[[], None]) -> None:
        self.run_timer(HumanTimingsService().get_timing_base_action(), step)

    def _on_step_finished(
        self, step_name: str, next_step: Callable[[], None], error_code: str | None
    ) -> None:
        if error_code is not None:
            self.logger.error(f"[SmokeTest] '{step_name}' failed with '{error_code}', aborting sequence")
            return self.finish(error_code)
        self.logger.info(f"[SmokeTest] '{step_name}' OK")
        self._next(next_step)

    def _on_farm_step_finished(
        self, step_name: str, next_step: Callable[[], None], error_code: str | None
    ) -> None:
        if error_code not in (None, BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED):
            self.logger.error(f"[SmokeTest] '{step_name}' failed with '{error_code}', aborting sequence")
            return self.finish(error_code)
        self._next(next_step)

    def step_fighter(self) -> None:
        self.fighter_behavior.start(
            area_id=SMOKE_TEST_HARVEST_AREA_ID,
            sub_area_id=SMOKE_TEST_HARVEST_SUB_AREA_ID,
            is_stopped_at_new_map_condition=lambda: self.fighter_behavior.fights_done > 0,
            callback=partial(self._on_farm_step_finished, "fighter", self.step_harvest_for_craft),
            parent=self,
        )

    def step_harvest_for_craft(self) -> None:
        self._smoke_test_recipe = self._get_smoke_test_recipe()
        if self._smoke_test_recipe is None:
            self.logger.info(
                "[SmokeTest] fixed recipe not craftable at current job level, skipping harvest+craft"
            )
            return self._next(self.step_bank)

        self.harvester_behavior.start(
            area_id=SMOKE_TEST_HARVEST_AREA_ID,
            sub_area_id=SMOKE_TEST_HARVEST_SUB_AREA_ID,
            is_stopped_at_new_map_condition=self._harvest_ingredients_collected,
            target_resource_item_ids=set(self._smoke_test_recipe.ingredientIds),
            callback=partial(self._on_farm_step_finished, "harvester", self.step_craft),
            parent=self,
        )

    def _harvest_ingredients_collected(self) -> bool:
        assert self._smoke_test_recipe is not None
        if self.harvester_behavior.collect_behavior.collects_done == 0:
            return False
        return all(
            self._inventory_quantity(ingredient_id) >= per_unit_qty * SMOKE_TEST_RECIPE_QUANTITY
            for ingredient_id, per_unit_qty in zip(
                self._smoke_test_recipe.ingredientIds, self._smoke_test_recipe.quantities
            )
        )

    def _inventory_quantity(self, gid: int) -> int:
        item = self.game_state.inventory.get_object_item_by_gid(gid)
        return item.item.quantity if item else 0

    def step_craft(self) -> None:
        assert self._smoke_test_recipe is not None
        self.craft_behavior.start(
            craft_requests=[
                CraftRequest(recipe=self._smoke_test_recipe, stop_condition=SMOKE_TEST_RECIPE_QUANTITY)
            ],
            callback=partial(self._on_step_finished, "craft", self.step_characteristic_upgrade),
            parent=self,
        )

    def step_characteristic_upgrade(self) -> None:
        request = build_characteristic_upgrade_request(
            self.game_state.fight.primary_and_second_elem[0], CHARACTERISTIC_UPGRADE_POINTS
        )
        self.event_manager.on(
            CharacterCharacteristicUpgradeResultEvent,
            self.on_characteristic_upgrade_result,
            originator=self,
            once=True,
            timeout=CHARACTERISTIC_UPGRADE_TIMEOUT_SECONDS,
            on_timeout=lambda: self.finish(SmokeTestErrorCode.CHARACTERISTIC_UPGRADE_TIMEOUT),
        )
        self.send_message_delayed(request, HumanTimingsService().get_timing_base_action())

    def on_characteristic_upgrade_result(self, msg: CharacterCharacteristicUpgradeResultEvent) -> None:
        Result = CharacterCharacteristicUpgradeResultEvent.CharacteristicUpgradeResult
        if msg.result not in (Result.SUCCESS, Result.NOT_ENOUGH_POINT):
            self.logger.error(f"[SmokeTest] characteristic upgrade unexpected result: {msg.result}")
            return self.finish(SmokeTestErrorCode.CHARACTERISTIC_UPGRADE_INCOHERENT)
        self.logger.info("[SmokeTest] 'characteristic_upgrade' OK")
        self._next(self.step_bank)

    def _get_smoke_test_recipe(self) -> RecipeItem | None:
        recipe = next((r for r in DataReader().recipes if r.resultId == SMOKE_TEST_RECIPE_RESULT_ID), None)
        if recipe is None:
            return None
        current_job_lvl = self.game_state.player.jobs_lvl_by_id.get(recipe.jobId, 0)
        if current_job_lvl < recipe.resultLevel:
            return None
        return recipe

    def step_bank(self) -> None:
        self.enter_bank_chest_behavior.start(
            callback=partial(self._on_step_finished, "bank", self.step_bank_roundtrip),
            parent=self,
        )

    def step_bank_roundtrip(self) -> None:
        item = next(iter(self.game_state.inventory.get_unlinked_objects()), None)
        if item is None:
            self.logger.info("[SmokeTest] no transferable item in inventory, skipping bank round-trip")
            return self._next(self.step_sale_hotel)

        self._bank_roundtrip_item_gid = item.item.gid
        self._bank_roundtrip_quantity = 1
        bank_item_before = self.game_state.inventory.get_bank_object_by_gid(item.item.gid)
        self._bank_roundtrip_bank_qty_before = bank_item_before.item.quantity if bank_item_before else 0

        self.event_manager.on(
            InventoryWeightEvent,
            self.on_bank_deposit_done,
            originator=self,
            once=True,
            timeout=BANK_ROUNDTRIP_TIMEOUT_SECONDS,
            on_timeout=lambda: self.finish(SmokeTestErrorCode.BANK_ROUNDTRIP_TIMEOUT),
        )
        req = ExchangeObjectMoveRequest(object_uid=item.item.uid, quantity=self._bank_roundtrip_quantity)
        self.send_message_delayed(req, HumanTimingsService().get_timing_base_action())

    def on_bank_deposit_done(self, _msg: InventoryWeightEvent) -> None:
        bank_item = self.game_state.inventory.get_bank_object_by_gid(self._bank_roundtrip_item_gid)
        expected_bank_qty = self._bank_roundtrip_bank_qty_before + self._bank_roundtrip_quantity
        if bank_item is None or bank_item.item.quantity != expected_bank_qty:
            self.logger.error(
                f"[SmokeTest] bank deposit inconsistent: expected {expected_bank_qty} in bank, "
                f"got {bank_item.item.quantity if bank_item else 0}"
            )
            return self.finish(SmokeTestErrorCode.BANK_ROUNDTRIP_INCOHERENT)

        self.event_manager.on(
            InventoryWeightEvent,
            partial(self.on_bank_withdraw_done, bank_item=bank_item),
            originator=self,
            once=True,
            timeout=BANK_ROUNDTRIP_TIMEOUT_SECONDS,
            on_timeout=lambda: self.finish(SmokeTestErrorCode.BANK_ROUNDTRIP_TIMEOUT),
        )
        req = ExchangeObjectMoveRequest(
            object_uid=bank_item.item.uid, quantity=-self._bank_roundtrip_quantity
        )
        self.send_message_delayed(req, HumanTimingsService().get_timing_base_action())

    def on_bank_withdraw_done(self, _msg: InventoryWeightEvent, bank_item: ObjectItemInventory) -> None:
        bank_item_after = self.game_state.inventory.get_bank_object_by_gid(self._bank_roundtrip_item_gid)
        bank_qty_after = bank_item_after.item.quantity if bank_item_after else 0
        inventory_item_after = self.game_state.inventory.get_object_item_by_gid(self._bank_roundtrip_item_gid)
        if bank_qty_after != self._bank_roundtrip_bank_qty_before or inventory_item_after is None:
            self.logger.error(
                f"[SmokeTest] bank withdraw inconsistent: expected {self._bank_roundtrip_bank_qty_before} "
                f"in bank (got {bank_qty_after}), and item back in inventory "
                f"(got {inventory_item_after})"
            )
            return self.finish(SmokeTestErrorCode.BANK_ROUNDTRIP_INCOHERENT)
        self.logger.info("[SmokeTest] 'bank_roundtrip' OK")
        self._next(self.step_sale_hotel)

    def step_sale_hotel(self) -> None:
        self.sale_hotel_sell_behavior.start(
            callback=partial(self._on_step_finished, "sale_hotel", self.step_sale_hotel_check),
            parent=self,
        )

    def step_sale_hotel_check(self) -> None:
        if self.sale_hotel_sell_behavior.activity_performed:
            hdv_by_uid = (
                GameDataController()
                .get_hdv_by_uid_by_player(self.game_state.player.server_id)
                .get(self.game_state.player.character_id, {})
            )
            if not hdv_by_uid:
                self.logger.error(
                    "[SmokeTest] sale hotel activity reported but no lot found for this character afterwards"
                )
                return self.finish(SmokeTestErrorCode.SALE_HOTEL_INCOHERENT)
        self._next(self.step_sale_hotel_buy)

    def step_sale_hotel_buy(self) -> None:
        if self._smoke_test_recipe is None:
            return self._next(self.step_quest)
        self.sale_hotel_buy_behavior.start(
            item_infos_to_buy=[
                ItemToBuyInfo(
                    item_gid=self._smoke_test_recipe.ingredientIds[0], max_kamas=SMOKE_TEST_BUY_MAX_KAMAS
                )
            ],
            category=CategoryItemEnum.RESOURCES,
            callback=partial(self._on_step_finished, "sale_hotel_buy", self.step_quest),
            parent=self,
        )

    def step_quest(self) -> None:
        self.quest_behavior.start(
            scripts=[QUEST_SCRIPTS[0]],
            callback=partial(self._on_step_finished, "quest", self.step_auto_equipment),
            parent=self,
        )

    def step_auto_equipment(self) -> None:
        self.auto_equipment_behavior.start(callback=self.finish, parent=self)
