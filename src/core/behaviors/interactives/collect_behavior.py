import random
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from dofus_unity_reader.grid.map_point import MapPoint
from datas.protos.non_obf.game.interactive_element_pb2 import (
    StatedElementUpdatedEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import (
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_change_behavior import MapChangeError
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.config import (
    BASE_RANGE,
    HARVEST_PAUSE_PROBABILITY,
    HARVEST_PAUSE_RANGE,
    LOOK_AROUND_PAUSE_RANGE,
    LOOK_AROUND_PROBABILITY,
)
from src.core.engine.interactives.collectable import Collectable
from src.core.engine.movements.map.path_finding.movement_path import MovementPath
from src.core.engine.movements.map.path_finding.path_finding import Pathfinding
from src.services.human_timings import HumanTimingsService


class CollectError(StrEnum):
    FULL_PODS = auto()


@dataclass
class CollectBehavior(Behavior):
    """collect all collectables in current map"""

    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding

    is_first_action: bool = field(init=False, default=False)

    excluded_element_ids: set[int] = field(init=False, default_factory=set[int])

    def run(self) -> None:
        self.excluded_element_ids.clear()
        self.is_first_action = True
        self.collect_map()

    def collect_map(self) -> None:
        if self.game_state.inventory.is_full_pods:
            return self.finish(CollectError.FULL_PODS)

        collectables = self.game_state.interactive.get_farmable_collectables(
            self.excluded_element_ids
        )
        if len(collectables) == 0:
            return self.finish()

        collectable_info = self.get_near_collectable(collectables)
        if collectable_info is None:
            return self.finish()

        move_path, collectable = collectable_info
        if self.is_first_action:
            self.is_first_action = False
            if random.random() < LOOK_AROUND_PROBABILITY:
                return self._do_look_around(move_path, collectable)
            self.run_timer(
                HumanTimingsService().get_timing_collect_on_new_map(),
                lambda: self.collect(move_path, collectable),
            )
        else:
            self.collect(move_path, collectable)

    def collect(self, move_path: MovementPath, collectable: Collectable) -> None:
        self.logger.info(f"Collecting at {move_path.end}")

        self.interactive_behavior.start(
            callback=partial(
                self.on_interactive_behavior_finished, collectable=collectable
            ),
            parent=self,
            move_path=move_path,
            element_id=collectable.interactive_element.element_id,
            skill_instance_uid=collectable.skill.skill_instance_uid,
        )

    def on_interactive_behavior_finished(
        self, error_code: str | None, collectable: Collectable
    ) -> None:
        if error_code in [InteractiveError.USE_ERROR, MapMoveError.REFUSED]:
            self.unregister_listener(
                StatedElementUpdatedEvent,
                reason="Interactive error, retrying collection without this listener",
            )
            self.excluded_element_ids.add(collectable.interactive_element.element_id)
            self.logger.info("Interactive error, trying to recollect on map.")
            return self.run_timer(BASE_RANGE, self.collect_map)
        elif error_code == MapChangeError.UNEXPECTED_NEW_MAP:
            return self.finish(error_code)

        self.event_manager.on(
            StatedElementUpdatedEvent,
            partial(
                self.on_stated_element_updated_event,
                element_id=collectable.interactive_element.element_id,
            ),
            originator=self,
        )

    def on_stated_element_updated_event(
        self, msg: StatedElementUpdatedEvent, element_id: int
    ) -> None:
        if (
            msg.stated_element.element_id == element_id
            and msg.stated_element.state == 1
        ):
            self.unregister_listener(
                StatedElementUpdatedEvent,
                reason="Element state confirmed, proceeding with collection",
            )
            if random.random() < HARVEST_PAUSE_PROBABILITY:
                pause_time = random.uniform(*HARVEST_PAUSE_RANGE)
                self.logger.debug(f"Taking a short break: {pause_time:.1f}s")
                self.run_timer(pause_time, self.collect_map)
            else:
                self.collect_map()

    def _do_look_around(
        self, move_path: MovementPath, collectable: Collectable
    ) -> None:
        adjacent_cell = self._get_random_walkable_cell_nearby()
        if adjacent_cell is None:
            return self.run_timer(
                HumanTimingsService().get_timing_collect_on_new_map(),
                lambda: self.collect(move_path, collectable),
            )

        self.logger.debug(f"Looking around at cell {adjacent_cell.cell_id}")
        look_path = self.path_finding.find_path(
            self.game_state.get_map_movement_context(),
            self.game_state.map.map_point,
            {adjacent_cell},
        )
        if look_path.end.cell_id != adjacent_cell.cell_id:
            return self.run_timer(
                HumanTimingsService().get_timing_collect_on_new_map(),
                lambda: self.collect(move_path, collectable),
            )

        def on_look_around_finished(_error_code: str | None) -> None:
            self.run_timer(
                random.uniform(*LOOK_AROUND_PAUSE_RANGE),
                lambda: self.collect(move_path, collectable),
            )

        self.interactive_behavior.map_move_behavior.start(
            callback=on_look_around_finished,
            parent=self,
            move_path=look_path,
        )

    def _get_random_walkable_cell_nearby(self) -> MapPoint | None:
        current_mp = self.game_state.map.map_point
        reachable_cells: list[MapPoint] = []

        candidates: set[MapPoint] = set()
        visited: set[MapPoint] = {current_mp}
        frontier: set[MapPoint] = set(current_mp.side_map_points)

        for _ in range(10):
            if not frontier:
                break
            candidates.update(frontier)
            next_frontier: set[MapPoint] = set()
            for mp in frontier:
                if mp not in visited:
                    visited.add(mp)
                    next_frontier.update(mp.side_map_points - visited)
            frontier = next_frontier

        for mp in candidates:
            path = self.path_finding.find_path(
                self.game_state.get_map_movement_context(), current_mp, {mp}
            )
            if path.end.cell_id == mp.cell_id:
                reachable_cells.append(mp)

        if not reachable_cells:
            return None
        return random.choice(reachable_cells)

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        near_coll_info: tuple[MovementPath, Collectable, float] | None = None
        for collectable in collectables:
            coll_move_path = self.path_finding.get_interactive_near_path(
                self.game_state.get_map_movement_context(),
                self.game_state.map.map_point,
                collectable.mp,
                skill_ids=[collectable.skill.skill_id],
            )
            if coll_move_path is None:
                continue
            coll_cost = MovementPath.get_total_duration(
                coll_move_path.path,
                self.game_state.inventory.inventory_weight,
                self.game_state.inventory.weight_max,
            )
            if near_coll_info is None or near_coll_info[2] > coll_cost:
                near_coll_info = (coll_move_path, collectable, coll_cost)
                if coll_cost == 0:
                    break

        if near_coll_info is None:
            return None

        return near_coll_info[0], near_coll_info[1]
