from collections.abc import Callable
from dataclasses import dataclass, field

from context_pb2 import ContextCreationEvent
from datas.protos.non_obf.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    ObjectUseRequest,
)
from dofus_unity_reader.data_center.data_reader import DataReader

from src.controller.game_data import GameDataController
from src.core.behaviors.farms.base_farm_behavior import BaseFarmBehavior
from src.core.behaviors.farms.fight.fight_behavior import FightBehavior
from src.core.behaviors.interactives.collect_behavior import (
    CollectBehavior,
    CollectError,
)
from src.core.behaviors.movements.auto_trip.auto_trip_behavior import (
    AutoTripErrorCode,
)
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.engine.weights.harvester.explorator import get_map_ids_to_explore
from src.core.engine.weights.harvester.weight_map import (
    get_harvester_additional_weight_by_map_id,
)
from src.services.human_timings import HumanTimingsService


@dataclass
class HarvesterBehavior(BaseFarmBehavior):
    """Behavior that automatically collect collectable in map, move to the next collectable or map"""

    collect_behavior: CollectBehavior
    fight_behavior: FightBehavior

    map_ids_to_explore: set[int] = field(init=False, default_factory=set[int])

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        is_stopped_at_new_map_condition: Callable[[], bool] | None = None,
    ) -> None:
        area_name = DataReader().area_by_id[area_id].nameId if area_id else "Unknown"
        subarea_name = DataReader().sub_area_by_id[sub_area_id].nameId if sub_area_id else "Unknown"
        self.logger.info(
            f"Starting harvesting in {area_name} / {subarea_name} (area_id={area_id}, subarea_id={sub_area_id})"
        )

        self.is_stopped_at_new_map_condition = is_stopped_at_new_map_condition
        self.map_ids_to_explore = get_map_ids_to_explore(self.random_farm_behavior.map_ids)
        self.logger.info(
            f"Will explore {len(self.map_ids_to_explore)} new maps in zone of {len(self.random_farm_behavior.map_ids)} total maps"
        )

        self.random_farm_behavior.init_random_farm(
            area_id,
            sub_area_id,
            lambda map_id: get_harvester_additional_weight_by_map_id(
                map_id,
                self.map_ids_to_explore,
                self.game_state.player.jobs_lvl_by_id,
                self.game_state.guild_chest.storage.get_all_items_by_gid(),
                self.game_state.player.is_sub,
                self.game_state.player.server_id,
            ),
        )
        self.init_listeners()
        if self.game_state.inventory.is_full_pods:
            self.logger.info(
                f"Inventory full ({self.game_state.inventory.pod_percentage}%), triggering unload"
            )
            return self.on_full_pods()
        self.on_new_map()

    def init_listeners(self) -> None:
        self.event_manager.on(ContextCreationEvent, self.on_context_creation_event, originator=self)

    def run_next_step(self) -> None:
        self.random_farm_behavior.start(callback=self.on_random_farm_behavior_finished, parent=self)

    def on_random_farm_behavior_finished(self, error_code: str | None) -> None:
        if error_code is EdgeError.NO_VALID_TRANSITION:
            return self.run_next_step()
        elif error_code in [
            MapChangeError.UNEXPECTED_NEW_MAP,
            EdgeError.INVALID_STARTING_MAP,
        ]:
            return self.on_unexpected_new_map()
        if error_code is AutoTripErrorCode.PATH_NOT_FOUND:
            return self.finish(error_code)
        self.raise_if_error(error_code)
        self.on_new_map()

    def on_unexpected_new_map(self) -> None:
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=lambda _: self.on_new_map(),
            originator=self,
            once=True,
            override_on_self=True,
        )

    def on_new_map(self) -> None:
        if self.game_state.map.map_id in self.map_ids_to_explore:
            remaining = len(self.map_ids_to_explore) - 1
            self.logger.info(
                f"New map explored: map_id={self.game_state.map.map_id} ({remaining} unexplored remaining)"
            )
            self.map_ids_to_explore.remove(self.game_state.map.map_id)
            GameDataController().add_map_id_checked(self.game_state.map.map_id)
            self.random_farm_behavior.additional_weight_by_map_id.pop(self.game_state.map.map_id, None)

        if self.check_stop_condition():
            return

        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.collect_behavior.start(callback=self.on_collect_behavior_finished, parent=self)
        else:
            self.run_next_step()

    def on_collect_behavior_finished(self, error_code: str | None) -> None:
        if error_code == CollectError.FULL_PODS:
            return self.on_full_pods()
        if error_code == MapChangeError.UNEXPECTED_NEW_MAP:
            return self.on_unexpected_new_map()
        self.raise_if_error(error_code)
        self.run_next_step()

    def on_context_creation_event(self, msg: ContextCreationEvent) -> None:
        if msg.context != ContextCreationEvent.GameContext.FIGHT:
            return
        with self.event_manager.lock:
            self.clear_behavior()
            self.init_listeners()
            self.fight_behavior.start(callback=self.on_fight_behavior_finished, parent=self)

    def on_fight_behavior_finished(self, error_code: str | None) -> None:
        self.raise_if_error(error_code)
        self.purge_inventory()

    def purge_inventory(self) -> None:
        self.logger.info("Purging inventory from harvest bags")
        for object in self.game_state.inventory.objects_by_uid.values():
            # clear inventory from resource bag
            if object.item.gid not in DataReader().item_by_id:
                continue

            type_item = DataReader().item_by_id[object.item.gid].typeId
            if type_item == 100:
                # sac de ressource
                def use_harvest_bag():
                    req = ObjectUseRequest(object_uid=object.item.uid)
                    self.event_manager.send(req)
                    self.run_timer(
                        HumanTimingsService().get_timing_before_item_use(), lambda: self.purge_inventory()
                    )

                return self.run_timer(HumanTimingsService().get_timing_base_action(), use_harvest_bag)

        self.run_timer(HumanTimingsService().get_timing_base_action(), self.on_fight_end_after_purge)

    def on_fight_end_after_purge(self) -> None:
        self.logger.info("Purge of harvest bag is finished, let's continue")
        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()
        self.on_new_map()
