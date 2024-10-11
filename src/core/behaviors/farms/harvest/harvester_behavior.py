from dataclasses import dataclass, field

from protos.game.inventory_pb2 import (
    ObjectUseRequest,
    ObjectUseMultipleRequest,
    ObjectDeletedEvent,
)
from protos.game.job_pb2 import JobExperiencesUpdateEvent
from src.const import FAKE_INFINITY_VALUE
from src.core.behaviors.bank.unload_behavior import UnloadBehavior
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.harvest.collect_behavior import (
    CollectBehavior,
    CollectError,
)
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.fight.fight_behavior import FightBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.data_center.data_reader import DataReader
from src.core.logic.farmer.collectables import add_collectable_map_checked
from src.core.logic.farmer.jobs import HARVESTER_JOB_IDS
from src.core.logic.farmer.weight_collectables import (
    get_additional_weight_by_map_id,
    get_map_ids_to_explore,
)
from src.core.logic.world.world_path_finder import WorldPathFinder
from src.exceptions import UnhandledErrorCodeException
from src.interfaces.enums.priority import PriorityEnum


@dataclass
class HarvesterBehavior(Behavior):
    """random harvest in zone"""

    auto_trip_smart_behavior: AutoTripSmartBehavior
    world_path_finder: WorldPathFinder
    random_farm_behavior: RandomFarmBehavior
    collect_behavior: CollectBehavior
    fight_behavior: FightBehavior
    unload_behavior: UnloadBehavior

    map_ids_to_explore: set[int] = field(init=False, default_factory=set)

    def run(self, area_id: int | None, sub_area_id: int | None):
        self.random_farm_behavior.init_random_farm(area_id, sub_area_id)
        self.map_ids_to_explore = get_map_ids_to_explore(
            self.random_farm_behavior.map_ids
        )
        self.refresh_weight_map_ids()
        self.event_manager.on(
            JobExperiencesUpdateEvent,
            self.on_job_experiences_update_event,
            originator=self,
            priority=PriorityEnum.MAX,
        )

        if self.game_state.inventory.is_full_pods:
            return self.on_full_pods()

        self.on_new_map()

    def refresh_weight_map_ids(self):
        self.random_farm_behavior.additional_weight_by_map_id = (
            get_additional_weight_by_map_id(
                self.random_farm_behavior.map_ids,
                self.game_state.player.jobs_lvl_by_id,
            )
        )
        for map_id in self.map_ids_to_explore:
            self.random_farm_behavior.additional_weight_by_map_id[map_id] = (
                FAKE_INFINITY_VALUE
            )

    def on_unload_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_new_map()

    def run_next_step(self):
        self.random_farm_behavior.start(
            callback=self.on_random_farm_behavior_finished, parent=self
        )

    def on_random_farm_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            if error_code is EdgeError.INVALID_TRANSITION:
                return self.run_next_step()
            elif error_code is EdgeError.WAS_ATTACKED:
                return self.on_attacked()
            raise UnhandledErrorCodeException(error_code)
        if self.game_state.map.map_id in self.map_ids_to_explore:
            self.map_ids_to_explore.remove(self.game_state.map.map_id)
            add_collectable_map_checked(self.game_state.map.map_id)
            self.refresh_weight_map_ids()
        self.on_new_map()

    def on_attacked(self):
        self.fight_behavior.start(callback=self.on_fight_behavior_finished, parent=self)

    def on_fight_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.on_fight_end()

    def on_fight_end(self):
        for object in self.game_state.inventory.objects_by_uid.values():
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
                    lambda _: self.on_fight_end(),
                    originator=self,
                    once=True,
                )
                self.run_timer((0.1, 0.3), lambda: self.event_manager.send(req))
                break
        else:
            self.on_new_map()

    def on_new_map(self):
        if self.game_state.map.map_id in self.random_farm_behavior.map_ids:
            self.collect_behavior.start(
                callback=self.on_collect_behavior_finished, parent=self
            )
        else:
            self.run_next_step()

    def on_collect_behavior_finished(self, error_code: str | None):
        if error_code == CollectError.FULL_PODS:
            return self.on_full_pods()
        elif error_code is CollectError.WAS_ATTACKED:
            return self.on_attacked()
        elif error_code is not None:
            raise UnhandledErrorCodeException(error_code)
        self.run_next_step()

    def on_full_pods(self):
        if self.game_state.player.level < 10:
            self.logger.warning(
                f"Player can't unload because he is level {self.game_state.player.level}"
            )
            return self.finish()

        return self.unload_behavior.start(
            parent=self, callback=self.on_unload_behavior_finished
        )

    def on_job_experiences_update_event(self, msg: JobExperiencesUpdateEvent):
        if len(self.map_ids_to_explore) != 0:
            return

        if any(
            job_xp.job_level % 10 == 0
            and self.game_state.player.jobs_lvl_by_id.get(job_xp.job_id, 1)
            != job_xp.job_level
            and job_xp.job_id in HARVESTER_JOB_IDS
            for job_xp in msg.experiences
        ):
            # interesting lvl up, let's recalculate weight
            self.refresh_weight_map_ids()
