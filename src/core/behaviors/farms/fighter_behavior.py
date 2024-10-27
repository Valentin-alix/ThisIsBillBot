from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

from data_center.data_reader import DataReader

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.consts import USEFUL_UNLOAD
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.mule import BOT_KAMA_LIMIT_TO_GIVE
from src.core.config.timings import (
    get_time_beween_sale_hotel_prices,
)
from src.core.logic.flags.map_position_flags import allow_monster_agression
from src.core.logic.map.path_finding.path_finding import Pathfinding
from src.exceptions import UnhandledErrorCodeException


@dataclass
class FighterBehavior(Behavior):
    random_farm_behavior: RandomFarmBehavior
    unload_behavior: UnloadBehavior
    map_move_behavior: MapMoveBehavior
    path_finding: Pathfinding
    sale_hotel_prices_behavior: SaleHotelPricesBehavior
    attacker_behavior: AttackerBehavior
    mule_give_behavior: MuleGiveBehavior

    _stop_condition_with_callback: (
        tuple[Callable[[], bool], Callable[[], None]] | None
    ) = field(init=False, default=None)
    _timedelta_for_sale_hotel_prices: timedelta = field(
        init=False, default_factory=get_time_beween_sale_hotel_prices
    )

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        stop_condition_with_callback: tuple[Callable[[], bool], Callable[[], None]]
        | None = None,
    ):
        self._stop_condition_with_callback = stop_condition_with_callback
        self.random_farm_behavior.init_random_farm(
            area_id, sub_area_id, self.get_additional_weight_by_map_id
        )
        self.on_new_map()

    def on_new_map(self):
        if self._stop_condition_with_callback is not None:
            stop_condition, callback = self._stop_condition_with_callback
            if stop_condition():
                self.logger.info("Stop condition triggered, let's call callback")
                self.finish()
                return callback()

        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.attacker_behavior.start(
                callback=self.on_attacker_behavior_finish, parent=self
            )
        else:
            self.run_next_step()

    def run_next_step(self):
        self.random_farm_behavior.start(
            parent=self, callback=self.on_random_farm_behavior_finished
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if (
            error_code is not None
            and error_code is not MapChangeError.UNEXPECTED_NEW_MAP
        ):
            if error_code is EdgeError.NO_VALID_TRANSITION:
                return self.run_next_step()
            raise UnhandledErrorCodeException(error_code)
        self.on_new_map()

    def on_attacker_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        if self.game_state.inventory.is_full_pods:
            self.on_full_pods()
        else:
            self.run_next_step()

    def on_full_pods(self):
        if self.game_state.inventory.kamas > BOT_KAMA_LIMIT_TO_GIVE or (
            self.game_state.player.is_full_object_in_sale_hotel
            and (
                datetime.now() - self.game_state.sale_hotel.last_time_updated_prices
                < self._timedelta_for_sale_hotel_prices
            )
        ):
            self.mule_give_behavior.start(
                callback=self.on_unloaded_on_mule_finished, parent=self
            )
        else:
            self.unload_behavior.start(parent=self, callback=self.on_unload_finished)

    def on_unloaded_on_mule_finished(self, error_code: str | None):
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            self.unload_behavior.start(parent=self, callback=self.on_unload_finished)
        else:
            self.on_new_map()

    def on_unload_finished(self, error_code: str | None):
        if error_code is not None:
            self.logger.error("Can't unload")
            return self.finish(error_code)
        if (
            datetime.now() - self.game_state.sale_hotel.last_time_updated_prices
            > self._timedelta_for_sale_hotel_prices
        ):
            self._timedelta_for_sale_hotel_prices = get_time_beween_sale_hotel_prices()
            self.sale_hotel_prices_behavior.start(
                callback=lambda _: self.on_new_map(), parent=self
            )
        else:
            self.on_new_map()

    def get_additional_weight_by_map_id(self, map_id: int):
        map_pos_data = DataReader().map_pos_by_map_id[map_id]
        m_flags = map_pos_data.m_flags
        if not allow_monster_agression(m_flags):
            weight = 0
        else:
            sub_area_lvl = DataReader().sub_area_by_id[map_pos_data.subAreaId].level
            weight = 1000 / (1 + abs(sub_area_lvl - self.game_state.player.level))
        return weight
