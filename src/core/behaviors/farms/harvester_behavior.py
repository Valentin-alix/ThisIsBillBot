from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable

from d3_mapping.resources.protos.game.context_pb2 import ContextCreationEvent
from d3_mapping.resources.protos.game.inventory_pb2 import (
    ObjectDeletedEvent,
    ObjectUseMultipleRequest,
    ObjectUseRequest,
)
from d3_mapping.resources.protos.game.job_pb2 import JobExperiencesUpdateEvent
from data_center.data_reader import DataReader

from src.const import FAKE_INFINITY_VALUE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.interactives.collect_behavior import (
    CollectBehavior,
    CollectError,
)
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.mule_kamas.mule_give_kamas_behavior import MuleGiveKamasBehavior
from src.core.behaviors.sale_hotel.sale_hotel_prices_behavior import (
    SaleHotelPricesBehavior,
)
from src.core.behaviors.storage.unloads.unload_behavior import UnloadBehavior
from src.core.config.mule_kamas import (
    BOT_KAMA_LIMIT_TO_GIVE,
    BOT_MINIMAL_KAMAS,
    MULE_BANK_CHARACTER_ID,
)
from src.core.config.timings import (
    BASE_RANGE,
    get_time_beween_sale_hotel_prices,
)
from src.core.controller.gfx_mapping import GfxMappingController
from src.core.controller.sale_hotel import SaleHotelController
from src.core.logic.farmer.weight_collectables import (
    get_map_id_collectable_weight,
    get_map_ids_to_explore,
    is_interesting_job_lvl_up_for_weight,
)
from src.core.states.guild_chest_state import CHEST_OBJECT_BY_GID_BY_TAB
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class HarvesterBehavior(Behavior):
    """random harvest in zone"""

    random_farm_behavior: RandomFarmBehavior
    collect_behavior: CollectBehavior
    fight_behavior: FightBehavior
    unload_behavior: UnloadBehavior
    sale_hotel_prices_behavior: SaleHotelPricesBehavior
    mule_give_kamas_behavior: MuleGiveKamasBehavior

    map_ids_to_explore: set[int] = field(init=False, default_factory=set)

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
        self.logger.info(
            f"Harvester is going to area {area_id} with subarea_id {sub_area_id}"
        )
        self._stop_condition_with_callback = stop_condition_with_callback
        self.random_farm_behavior.init_random_farm(
            area_id, sub_area_id, self.get_additional_weight_by_map_id
        )
        self.map_ids_to_explore = get_map_ids_to_explore(
            self.random_farm_behavior.map_ids
        )
        self.event_manager.on(
            JobExperiencesUpdateEvent,
            self.on_job_experiences_update_event,
            originator=self,
            priority=PriorityEnum.MAX,
        )
        self.event_manager.on(
            ContextCreationEvent, self.on_context_creation_event, originator=self
        )

        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()
        self.on_new_map()

    def get_additional_weight_by_map_id(self, map_id: int):
        if map_id in self.map_ids_to_explore:
            return FAKE_INFINITY_VALUE
        gfx_to_item_and_job = GfxMappingController().get_item_job_by_gfx()
        storage_by_gid = {
            object.item.gid: object
            for objects in CHEST_OBJECT_BY_GID_BY_TAB.values()
            for object in objects.values()
        }
        avg_price_by_gid = SaleHotelController().get_avg_price_by_gid()
        weight = get_map_id_collectable_weight(
            map_id,
            gfx_to_item_and_job,
            self.game_state.player.jobs_lvl_by_id,
            storage_by_gid,
            avg_price_by_gid,
            self.game_state.player.is_sub,
        )
        return weight

    def run_next_step(self):
        self.random_farm_behavior.start(
            callback=self.on_random_farm_behavior_finished, parent=self
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if (
            error_code is not None
            and error_code is not MapChangeError.UNEXPECTED_NEW_MAP
        ):
            if error_code is EdgeError.NO_VALID_TRANSITION:
                return self.run_next_step()
            raise UnhandledErrorCodeException(error_code)
        if self.game_state.map.map_id in self.map_ids_to_explore:
            self.logger.info("New map explored adding to map checked")
            self.map_ids_to_explore.remove(self.game_state.map.map_id)
            GfxMappingController().add_map_id_checked(self.game_state.map.map_id)
            self.random_farm_behavior.additional_weight_by_map_id.pop(
                self.game_state.map.map_id, None
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
        self.run_next_step()

    def on_context_creation_event(self, msg: ContextCreationEvent):
        if msg.context != ContextCreationEvent.GameContext.FIGHT:
            return
        if self.random_farm_behavior.is_running.is_set():
            self.random_farm_behavior.stop()
        if self.unload_behavior.is_running.is_set():
            self.unload_behavior.stop()
        if self.sale_hotel_prices_behavior.is_running.is_set():
            self.sale_hotel_prices_behavior.stop()
        if self.collect_behavior.is_running.is_set():
            self.collect_behavior.stop()
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
                if object.item.quantity > 1:
                    req = ObjectUseMultipleRequest(
                        object_uid=object.item.uid, quantity=object.item.quantity
                    )
                else:
                    req = ObjectUseRequest(object_uid=object.item.uid)

                self.event_manager.on(
                    ObjectDeletedEvent,
                    lambda _: self.purge_inventory(),
                    originator=self,
                    once=True,
                )
                return self.run_timer(BASE_RANGE, lambda: self.event_manager.send(req))
        self.on_fight_end_after_purge()

    def on_fight_end_after_purge(self):
        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()
        self.on_new_map()

    def on_full_pods(self):
        self.unload_behavior.start(
            parent=self, callback=self.on_unload_behavior_finished
        )

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            self.logger.error("Can't unload")
            return self.finish(error_code)
        if (
            datetime.now() - self.game_state.sale_hotel.last_time_updated_prices
            > self._timedelta_for_sale_hotel_prices
        ):
            self._timedelta_for_sale_hotel_prices = get_time_beween_sale_hotel_prices()
            self.sale_hotel_prices_behavior.start(
                callback=lambda _: self.on_sale_hotel_price_updated_and_unloaded(),
                parent=self,
            )
        else:
            self.on_new_map()

    def on_sale_hotel_price_updated_and_unloaded(self):
        if (
            MULE_BANK_CHARACTER_ID is not None
            and self.game_state.inventory.kamas >= BOT_KAMA_LIMIT_TO_GIVE
        ):
            self.mule_give_kamas_behavior.start(
                kamas=self.game_state.inventory.kamas - BOT_MINIMAL_KAMAS,
                callback=lambda _: self.on_new_map(),
                parent=self,
            )
        else:
            self.on_new_map()

    def on_job_experiences_update_event(self, msg: JobExperiencesUpdateEvent):
        if is_interesting_job_lvl_up_for_weight(
            msg, self.game_state.player.jobs_lvl_by_id
        ):
            # interesting lvl up, let's recalculate weights
            self.random_farm_behavior.additional_weight_by_map_id.clear()
