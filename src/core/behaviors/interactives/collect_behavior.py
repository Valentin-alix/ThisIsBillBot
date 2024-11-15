from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import partial

from d3_mapping.resources.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
    MapCurrentEvent,
)
from d3_mapping.resources.protos.game.interactive_element_pb2 import (
    StatedElementUpdatedEvent,
)

from src.controller.human_timings import HumanTimingsController
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import (
    InteractiveBehavior,
    InteractiveError,
)
from src.core.behaviors.movements.map_move_behavior import MapMoveError
from src.core.config.timings import BASE_RANGE
from src.core.logic.map.path_finding.movement_path import MovementPath
from src.core.logic.map.path_finding.path_finding import Pathfinding
from src.interfaces.models.collectable import Collectable


class CollectError(StrEnum):
    FULL_PODS = auto()


@dataclass
class CollectBehavior(Behavior):
    """collect all collectables in current map"""

    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding

    is_first_action: bool = field(init=False, default=False)

    excluded_element_ids: set[int] = field(init=False, default_factory=set)

    def run(self) -> None:
        self.excluded_element_ids.clear()
        self.is_first_action = True
        self.event_manager.on(
            MapCurrentEvent, self.on_map_current_event, originator=self, once=True
        )
        self.collect_map()

    def on_map_current_event(self, msg: MapCurrentEvent):
        self.event_manager.on(
            FightMapInformationEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
        )
        self.event_manager.on(
            MapComplementaryInformationEvent,
            lambda _: self.finish(),
            originator=self,
            once=True,
        )

    def collect_map(self):
        if self.game_state.map._is_in_map_transition:
            return

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
            self.run_timer(
                HumanTimingsController().get_timing_collect_on_new_map(),
                lambda: self.collect(move_path, collectable),
            )
        else:
            self.collect(move_path, collectable)

    def collect(self, move_path: MovementPath, collectable: Collectable):
        self.logger.info(f"Collecting at {move_path.end}")
        self.event_manager.on(
            StatedElementUpdatedEvent,
            partial(
                self.on_interactive_updated,
                element_id=collectable.interactive_element.element_id,
            ),
            originator=self,
        )
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
    ):
        if error_code in [InteractiveError.USE_ERROR, MapMoveError.REFUSED]:
            self.event_manager.clear_listener_by_origin_and_type(
                StatedElementUpdatedEvent, originator=self
            )
            self.excluded_element_ids.add(collectable.interactive_element.element_id)
            self.logger.warning("Interactive error, trying to recollect on map.")
            return self.run_timer(BASE_RANGE, self.collect_map)

    def on_interactive_updated(self, msg: StatedElementUpdatedEvent, element_id: int):
        if (
            msg.stated_element.element_id == element_id
            and msg.stated_element.state == 1
        ):
            self.event_manager.clear_listener_by_origin_and_type(
                StatedElementUpdatedEvent, originator=self
            )
            self.collect_map()

    def get_near_collectable(
        self,
        collectables: list[Collectable],
    ) -> tuple[MovementPath, Collectable] | None:
        near_coll_info: tuple[MovementPath, Collectable, float] | None = None
        for collectable in collectables:
            coll_move_path = self.path_finding.get_interactive_near_path(
                self.game_state.player.map_point,
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
