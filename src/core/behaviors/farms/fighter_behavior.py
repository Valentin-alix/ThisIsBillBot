from dataclasses import dataclass
from functools import partial
from typing import Callable

from src.core.behaviors.farms.base_farm_behavior import BaseFarmBehavior
from src.core.behaviors.farms.fight.attacker_behavior import AttackerBehavior
from src.core.behaviors.movements.edge_behavior import EdgeError
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.core.engine.weights.fighter.weight_map import get_additional_weight_by_map_id


@dataclass
class FighterBehavior(BaseFarmBehavior):
    map_move_behavior: MapMoveBehavior
    path_finding: Pathfinding
    attacker_behavior: AttackerBehavior

    def run(
        self,
        area_id: int | None,
        sub_area_id: int | None,
        is_stopped_at_new_map_condition: Callable[[], bool] | None = None,
    ):
        self.is_stopped_at_new_map_condition = is_stopped_at_new_map_condition
        self.random_farm_behavior.init_random_farm(
            area_id,
            sub_area_id,
            partial(get_additional_weight_by_map_id, game_state=self.game_state),
        )
        self.on_new_map()

    def on_new_map(self):
        if self.check_stop_condition():
            return

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
            self.raise_if_error(error_code)
        self.on_new_map()

    def on_attacker_behavior_finish(
        self, error_code: str | None, count_fighted_on_map: int
    ):
        self.raise_if_error(error_code)
        if self.game_state.inventory.is_full_pods:
            self.on_full_pods()
        else:
            self.run_next_step()
