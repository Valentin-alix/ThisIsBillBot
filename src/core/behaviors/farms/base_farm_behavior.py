from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.equipment.auto_equipment_behavior import (
    AutoEquipmentBehavior,
)
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.sale_hotel.sale_hotel_sell_behavior import (
    SaleHotelSellBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_bank_chest_behavior import (
    EnterBankChestErrorCode,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestError,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import DO_CRAFT, DO_SALE_HOTEL
from src.core.engine.crafts.recipes import (
    get_recipes_for_job_lvl_upor_benefice,
    is_not_valid_recipe_for_lvl_up_job_or_benefice,
)
from src.core.engine.storage.unload import do_unload_on_mule


class BaseFarmingErrorCode(StrEnum):
    STOP_CONDITION_TRIGGERED = auto()


@dataclass
class BaseFarmBehavior(Behavior, ABC):
    """Abstract behavior that is used to automatically unload when full pods, then craft items to lvl up jobs, then sell & update items in sale hotel"""

    auto_equipment_behavior: AutoEquipmentBehavior
    random_farm_behavior: RandomFarmBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelSellBehavior
    mule_give_behavior: MuleGiveBehavior
    craft_behavior: CraftBehavior

    is_stopped_at_new_map_condition: Callable[[], bool] | None = field(init=False, default=None)

    @abstractmethod
    def on_new_map(self):
        pass

    @abstractmethod
    def run_next_step(self):
        pass

    def check_stop_condition(self) -> bool:
        if self.is_stopped_at_new_map_condition is None:
            return False

        if self.is_stopped_at_new_map_condition():
            self.logger.info("Stop condition triggered, let's call callback")
            self.finish(BaseFarmingErrorCode.STOP_CONDITION_TRIGGERED)
            return True
        return False

    def on_full_pods(self):
        if not self.game_state.inventory.can_use_bank:
            self.logger.info("No bank access: stopping farming to switch mode")
            return self.finish(EnterBankChestErrorCode.NOT_ENOUGH_KAMAS)
        self.unload_behavior.start(parent=self, callback=self.on_unload_finished)

    def on_unload_finished(self, error_code: str | None) -> None:
        if error_code is not None:
            self.logger.error("Can't unload")
            return self.finish(error_code)

        self.auto_equipment_behavior.start(callback=self.on_auto_equipment_finished, parent=self)

    def on_auto_equipment_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.continue_after_unload()

    def continue_after_unload(self) -> None:
        if do_unload_on_mule(self.game_state.inventory.kamas, self.game_state.player.is_sub):
            self.mule_give_behavior.start(callback=self.on_unloaded_on_mule_finished, parent=self)
        else:
            self.on_unloaded_on_mule_finished(None)

    def on_unloaded_on_mule_finished(self, error_code: str | None):
        if self.game_state.sale_hotel.should_update_price:
            self.on_time_to_update_price()
        else:
            self.on_new_map()

    def on_time_to_update_price(self):
        if not DO_CRAFT:
            return self.on_craft_behavior_finished(None)

        recipes = get_recipes_for_job_lvl_upor_benefice(
            self.game_state.player.is_sub, self.game_state.player.jobs_lvl_by_id
        )
        self.craft_behavior.start(
            recipes=recipes,
            stop_craft_recipe_condition=partial(
                is_not_valid_recipe_for_lvl_up_job_or_benefice,
                is_sub=self.game_state.player.is_sub,
                jobs_lvl_by_id=self.game_state.player.jobs_lvl_by_id,
            ),
            callback=self.on_craft_behavior_finished,
            parent=self,
        )

    def on_craft_behavior_finished(self, error_code: str | None):
        if error_code is not None and error_code is not EnterGuildChestError.CANT_ACCESS_GUILD_CHEST:
            self.logger.warning(f"Craft behavior failed: {error_code}")

        if not DO_SALE_HOTEL:
            return self.on_new_map()

        def on_sale_hotel_prices_finished(error_code: str | None) -> None:
            if error_code is not None:
                return self.finish(error_code)
            self.on_new_map()

        self.sale_hotel_prices_behavior.start(callback=on_sale_hotel_prices_finished, parent=self)
