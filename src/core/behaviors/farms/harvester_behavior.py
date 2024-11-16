from dataclasses import dataclass, field
from functools import partial
from typing import Callable

from D3Database.data_center.data_reader import DataReader
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    ObjectUseRequest,
)
from src.controller.gfx_mapping import GfxMappingController
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.craft.craft_behavior import CraftBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.interactives.collect_behavior import (
    CollectBehavior,
    CollectError,
)
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.mule_storage.mule_give_behavior import (
    MuleGiveBehavior,
)
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestError,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config import (
    BASE_RANGE,
    DO_CRAFT,
    DO_SALE_HOTEL,
    USEFUL_UNLOAD,
)
from src.core.engine.crafts.recipes import (
    get_recipes_for_job_lvl_up,
    is_not_valid_recipe_for_lvl_up_job,
)
from src.core.engine.storage.unload import do_unload_on_mule
from src.core.engine.weights.harvester.explorator import get_map_ids_to_explore
from src.core.engine.weights.harvester.weight_map import (
    get_harvester_additional_weight_by_map_id,
)
from src.exceptions import UnhandledErrorCodeException


@dataclass
class HarvesterBehavior(Behavior):
    """random harvest in zone"""

    random_farm_behavior: RandomFarmBehavior
    collect_behavior: CollectBehavior
    fight_behavior: FightBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelPricesBehavior
    mule_give_behavior: MuleGiveBehavior
    craft_behavior: CraftBehavior

    map_ids_to_explore: set[int] = field(init=False, default_factory=set)

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
        self.logger.info(
            f"Harvester is going to area {area_id} with subarea_id {sub_area_id}"
        )
        self._stop_condition_with_callback = stop_condition_with_callback
        self.map_ids_to_explore = get_map_ids_to_explore(
            self.random_farm_behavior.map_ids
        )
        self.random_farm_behavior.init_random_farm(
            area_id,
            sub_area_id,
            partial(
                get_harvester_additional_weight_by_map_id,
                map_ids_to_explore=self.map_ids_to_explore,
                game_state=self.game_state,
            ),
        )
        self.event_manager.on(
            FightMapInformationEvent, lambda _: self.on_fight_aggro(), originator=self
        )

        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()
        self.on_new_map()

    def run_next_step(self):
        self.random_farm_behavior.start(
            callback=self.on_random_farm_behavior_finished, parent=self
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if error_code is EdgeError.NO_VALID_TRANSITION:
            return self.run_next_step()
        elif error_code is MapChangeError.UNEXPECTED_NEW_MAP:
            return self.on_unexpected_new_map()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_new_map()

    def on_unexpected_new_map(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=lambda _: self.on_new_map_completed_after_unexpected_error(),
            originator=self,
            once=True,
        )

    def on_new_map_completed_after_unexpected_error(self):
        self.event_manager.clear_listener_by_origin_and_type(
            MapComplementaryInformationEvent, self
        )
        self.on_new_map()

    def on_new_map(self):
        if self.game_state.map.map_id in self.map_ids_to_explore:
            self.logger.info("New map explored adding to map checked")
            self.map_ids_to_explore.remove(self.game_state.map.map_id)
            GfxMappingController().add_map_id_checked(self.game_state.map.map_id)
            self.random_farm_behavior.additional_weight_by_map_id.pop(
                self.game_state.map.map_id, None
            )

        if self._stop_condition_with_callback is not None:
            stop_condition, callback = self._stop_condition_with_callback
            if stop_condition():
                self.logger.info("Stop condition triggered, let's call callback")
                self.finish()
                return callback()

        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.collect_behavior.start(
                callback=self.on_collect_behavior_finished, parent=self
            )
        else:
            self.run_next_step()

    def on_collect_behavior_finished(self, error_code: str | None):
        if error_code == CollectError.FULL_PODS:
            return self.on_full_pods()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        if not self.game_state.fight.in_fight:
            self.run_next_step()

    def clear_running_behaviors(self):
        with self.event_manager.lock:
            if self.random_farm_behavior.is_running.is_set():
                self.random_farm_behavior.stop()
            if self.collect_behavior.is_running.is_set():
                self.collect_behavior.stop()
            if self.fight_behavior.is_running.is_set():
                self.fight_behavior.stop()
            if self.unload_behavior.is_running.is_set():
                self.unload_behavior.stop()
            if self.sale_hotel_prices_behavior.is_running.is_set():
                self.sale_hotel_prices_behavior.stop()
            if self.mule_give_behavior.is_running.is_set():
                self.mule_give_behavior.stop()
            if self.craft_behavior.is_running.is_set():
                self.craft_behavior.stop()

    def on_fight_aggro(self):
        self.event_manager.clear_listener_by_origin_and_type(
            MapComplementaryInformationEvent, self
        )
        self.clear_running_behaviors()
        self.fight_behavior.start(callback=self.on_fight_behavior_finished, parent=self)

    def on_fight_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.purge_inventory()

    def purge_inventory(self):
        for object in self.game_state.inventory.objects_by_uid.values():
            # clear inventory from resource bag
            type_item = DataReader().item_by_id[object.item.gid].typeId
            if type_item == 100:
                # sac de ressource
                def use_harvest_bag():
                    req = ObjectUseRequest(object_uid=object.item.uid)
                    self.game_state.inventory.objects_by_uid.pop(object.item.uid)
                    self.event_manager.send(req)
                    self.purge_inventory()

                return self.run_timer(BASE_RANGE, use_harvest_bag)

        self.run_timer(BASE_RANGE, self.on_fight_end_after_purge)

    def on_fight_end_after_purge(self):
        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()
        self.on_new_map()

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
        if (
            error_code is not None
            and error_code is not EnterGuildChestError.CANT_ACCESS_GUILD_CHEST
        ):
            raise UnhandledErrorCodeException(error_code)
        if not DO_SALE_HOTEL:
            return self.on_new_map()
        self.sale_hotel_prices_behavior.start(
            callback=lambda _: self.on_new_map(), parent=self
        )
