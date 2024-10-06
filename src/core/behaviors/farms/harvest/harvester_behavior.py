from collections import defaultdict
from dataclasses import dataclass, field

from src.consts import ON_NEW_MAP_BEFORE_ACTION
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.harvest.collect_behavior import CollectBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.repositories.data_reader import DataReader
from src.core.states.inventory_state import InventoryState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.interfaces.models.collectable import Collectable


@dataclass
class HarvesterBehavior(Behavior):
    random_farm_behavior: RandomFarmBehavior
    collect_behavior: CollectBehavior
    unload_in_bank_behavior: UnloadInBankBehavior
    path_finding: Pathfinding
    player_state: PlayerState
    inventory_state: InventoryState
    map_state: MapState

    _map_ids: set[int] = field(init=False, default_factory=set)

    def run(self):
        """random harvest in current sub area"""
        curr_sub_area = DataReader().map_pos_by_map_id[self.map_state.map_id].subAreaId
        self._map_ids = set(DataReader().sub_area_by_id[curr_sub_area].mapIds.Array)
        self.collect_map()

    def on_new_map(self):
        self.run_timer(ON_NEW_MAP_BEFORE_ACTION, self.collect_map)

    def collect_map(self):
        if self.inventory_state.is_full_pods:
            return self.unload_in_bank_behavior.start(
                parent=self, callback=self.on_unloaded_bank
            )

        collectables = self.player_state.get_farmable_collectables()
        if len(collectables) == 0:
            return self.random_farm_behavior.start(
                callback=lambda _: self.on_new_map(), parent=self, map_ids=self._map_ids
            )

        collectable_info = self.get_near_collectable(collectables)
        if collectable_info is None:
            return self.random_farm_behavior.start(
                callback=lambda _: self.on_new_map(), parent=self, map_ids=self._map_ids
            )

        move_path, collectable = collectable_info
        self.collect_behavior.start(
            callback=self.on_collected,
            parent=self,
            move_path=move_path,
            collectable=collectable,
        )

    def on_unloaded_bank(self, error_code: str | None):
        if error_code is not None:
            return
        self.on_new_map()

    def on_collected(self, error_code: str | None):
        if error_code is not None:
            return
        self.collect_map()

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:

        collectable_by_mp: dict[MapPoint, list[Collectable]] = defaultdict(list)

        for collectable in collectables:
            collectable_mp = MapPoint.from_cell_id(
                collectable.get_cell_id(self.map_state.map_id)
            )
            collectable_by_mp[collectable_mp].append(collectable)
            for map_point in collectable_mp.side_map_points:
                collectable_by_mp[map_point].append(collectable)

        move_path = self.path_finding.find_path(
            start=self.player_state.map_point,
            ends=set(collectable_by_mp.keys()),
        )
        for collectable in collectable_by_mp.get(move_path.end, []):
            mp_element = MapPoint.from_cell_id(
                collectable.get_cell_id(self.map_state.map_id)
            )
            skill_range = DataReader().skill_by_id[collectable.skill.skill_id].range
            if move_path.end.distance_to_map_point(mp_element) <= skill_range:
                return move_path, collectable

        return None
