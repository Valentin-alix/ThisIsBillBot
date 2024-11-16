from dataclasses import dataclass, field
from functools import partial
from typing import Callable

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.behaviors.mule_storage.mule_give_behavior import MuleGiveBehavior
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import (
    DO_CRAFT,
    DO_SALE_HOTEL,
    USEFUL_UNLOAD,
)
from src.core.engine.crafts.recipes import (
    get_recipes_for_job_lvl_up,
    is_not_valid_recipe_for_lvl_up_job,
)
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.storage.unload import do_unload_on_mule
from src.core.engine.weights.fighter.weight_map import (
    get_additional_weight_by_map_id,
)
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
    craft_behavior: CraftBehavior

    _stop_condition_with_callback: (
        tuple[Callable[[], bool], Callable[[], None]] | None
    ) = field(init=False, default=None)

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        stop_condition_with_callback: tuple[Callable[[], bool], Callable[[], None]]
        | None = None,
    ):
        self._stop_condition_with_callback = stop_condition_with_callback
        self.random_farm_behavior.init_random_farm(
            area_id,
            sub_area_id,
            partial(get_additional_weight_by_map_id, game_state=self.game_state),
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

    def on_attacker_behavior_finish(
        self, error_code: str | None, count_fighted_on_map: int
    ):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        if self.game_state.inventory.is_full_pods:
            self.on_full_pods()
        else:
            self.run_next_step()

    def on_full_pods(self):
        if do_unload_on_mule(self.game_state):
            self.mule_give_behavior.start(
                callback=self.on_unloaded_on_mule_finished, parent=self
            )
        else:
            self.unload_behavior.start(parent=self, callback=self.on_unload_finished)

    def on_unloaded_on_mule_finished(self, error_code: str | None):
        if self.game_state.inventory.pod_percentage > USEFUL_UNLOAD:
            self.unload_behavior.start(parent=self, callback=self.on_unload_finished)
        else:
            self.on_unload_finished(error_code)

    def on_unload_finished(self, error_code: str | None):
        if error_code is not None:
            self.logger.error("Can't unload")
            return self.finish(error_code)
        if self.game_state.sale_hotel.should_update_price:
            self.on_interesting_amount_of_farming_done()
        else:
            self.on_new_map()

    def on_interesting_amount_of_farming_done(self):
        if not DO_CRAFT:
            return self.on_craft_behavior_finished(None)
        recipes = get_recipes_for_job_lvl_up(
            self.game_state.player.is_sub, self.game_state.player.jobs_lvl_by_id
        )
        self.craft_behavior.start(
            recipes=recipes,
            stop_craft_recipe_condition=partial(
                is_not_valid_recipe_for_lvl_up_job,
                is_sub=self.game_state.player.is_sub,
                jobs_lvl_by_id=self.game_state.player.jobs_lvl_by_id,
            ),
            callback=self.on_craft_behavior_finished,
            parent=self,
        )

    def on_craft_behavior_finished(self, error_code: str | None):
        if not DO_SALE_HOTEL:
            return self.on_new_map()
        self.sale_hotel_prices_behavior.start(
            callback=lambda _: self.on_new_map(), parent=self
        )
