from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.challenge_pb2 import (
    ChallengeReadyRequest,
    ChallengeSelectionRequest,
)
from db_dofus_unity.protos.game.context_pb2 import EntitiesDispositionEvent
from db_dofus_unity.protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
    FightStartEvent,
)
from src.common.logger import Logger
from src.consts import SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_movement_behavior import FightMovementBehavior
from src.core.logic.grid.map_point import MapPoint
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.player_state import PlayerState


@dataclass
class FightPlacementBehavior(Behavior):
    player_state: PlayerState
    fight_state: FightState
    entity_state: EntityState
    fight_movement_behavior: FightMovementBehavior

    def run(self):
        self.event_manager.on(
            ChallengeSelectionRequest,
            self.on_challenge_selection_request,
            originator=self,
        )
        self.event_manager.on(
            FightStartEvent, lambda _: self.finish(), originator=self, once=True
        )

        near_possible_cell_id = self.choose_near_placement_cell_id()
        Logger().info(f"found near cell id to enemy : {near_possible_cell_id}")
        if self.player_state.map_point.cell_id != near_possible_cell_id:
            Logger().info(f"Moving to {near_possible_cell_id}")
            self.event_manager.on(
                EntitiesDispositionEvent,
                partial(
                    self.on_entity_disposition_event,
                    requested_cell_id=near_possible_cell_id,
                ),
                originator=self,
            )
            request = FightPlacementPositionRequest(
                cell_id=near_possible_cell_id, entity_id=self.player_state.character_id
            )
            self.event_manager.send(request)
        else:
            self.on_position_near_enemy()

    def on_position_near_enemy(self):
        request = ChallengeReadyRequest()
        self.event_manager.send(request)

    def on_challenge_selection_request(self, msg: ChallengeSelectionRequest):
        request = FightReadyRequest(is_ready=True)
        self.run_timer(SMALL_RANGE, lambda: self.event_manager.send(request))

    def on_entity_disposition_event(
        self, msg: EntitiesDispositionEvent, requested_cell_id: int
    ):
        for disposition in msg.dispositions:
            if not disposition.cell_id == requested_cell_id:
                continue
            self.event_manager.clear_listener_by_origin_and_type(
                EntitiesDispositionEvent, self
            )
            return self.run_timer(SMALL_RANGE, self.on_position_near_enemy)

    def choose_near_placement_cell_id(self) -> int:
        min_dist_possible_cell_id: tuple[int, float] | None = None

        for possible_cell_id in self.fight_state.fight_placement_possible_positions:
            mp_point_possible_cell = MapPoint.from_cell_id(possible_cell_id)
            near_enemy_with_dist = (
                self.fight_movement_behavior.find_near_enemy_with_dist(
                    mp_point_possible_cell
                )
            )
            if near_enemy_with_dist is None:
                continue
            _, _, cost_path = near_enemy_with_dist
            if (
                min_dist_possible_cell_id is None
                or cost_path < min_dist_possible_cell_id[1]
            ):
                min_dist_possible_cell_id = (possible_cell_id, cost_path)

        if min_dist_possible_cell_id is None:
            raise ValueError("no possible cell id at choosing near placement ?")

        return min_dist_possible_cell_id[0]
