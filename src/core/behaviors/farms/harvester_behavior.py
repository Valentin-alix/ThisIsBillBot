from dataclasses import dataclass

from src.common.logger import Logger
from src.core.behaviors.bank.unload_in_bank_behavior import UnloadInBankBehavior
from src.core.behaviors.behavior import EndCode
from src.core.behaviors.farms.collect_behavior import CollectBehavior
from src.core.behaviors.farms.random_farm_behavior import RandomFarmBehavior
from src.core.behaviors.movements.auto_trip_behavior import AutoTripBehavior
from src.core.logic.grid.path_finding.movement_path import MovementPath
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.inventory_state import InventoryState
from src.core.states.player_state import PlayerState
from src.interfaces.models.collectable import Collectable


@dataclass
class HarvesterBehavior(RandomFarmBehavior):
    collect_behavior: CollectBehavior
    auto_trip_behavior: AutoTripBehavior
    unload_in_bank_behavior: UnloadInBankBehavior
    path_finding: Pathfinding
    player_state: PlayerState
    inventory_state: InventoryState

    def run(self):
        self.collect_all()

    def collect_all(self):
        if self.inventory_state.is_full_pods:
            self.unload_in_bank_behavior.start(
                parent=self, callback=self.on_unloaded_bank
            )
            return

        collectables = self.player_state.get_farmable_collectables()
        collectable_info = self.get_near_collectable(collectables)
        if collectable_info is None:
            next_map_id = self.get_random_next_map_id()
            Logger().info(f"No collectable found at this map, moving to {next_map_id}")
            self.auto_trip_behavior.start(
                callback=self.on_new_map, parent=self, map_id=next_map_id
            )
        else:
            move_path, collectable = collectable_info
            self.collect_behavior.start(
                callback=self.on_collected,
                parent=self,
                move_path=move_path,
                collectable=collectable,
            )

    def on_unloaded_bank(self, code: EndCode):
        if code is not EndCode.SUCCESS:
            return
        self.collect_all()

    def on_new_map(self, code: EndCode):
        if code is not EndCode.SUCCESS:
            return
        self.collect_all()

    def on_collected(self, code: EndCode):
        if code is not EndCode.SUCCESS:
            return
        self.collect_all()

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        curr_mp = self.player_state.map_point

        near_collectable = min(
            collectables,
            key=lambda collectable: curr_mp.distance_to_cell_id(
                collectable.get_cell_id(self.map_state.map_id)
            ),
            default=None,
        )
        if near_collectable is None:
            return None
        move_path = self.path_finding.get_near_path_to_interactive(
            near_collectable.interactive_element.element_id,
            near_collectable.skill.skill_id,
        )
        return (move_path, near_collectable) if move_path else None
