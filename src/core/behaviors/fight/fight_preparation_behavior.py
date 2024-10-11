from dataclasses import dataclass
from functools import partial

from protos.game.context_pb2 import EntitiesDispositionEvent
from protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
    FightStartEvent,
)
from src.const import ON_CHALLENGE, ON_PLAYER_MOVED
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_challenge_behavior import FightChallengeBehavior
from src.core.behaviors.fight.fight_movement_behavior import FightMovementBehavior
from src.core.logic.grid.map_point import MapPoint
from src.exceptions import UnhandledErrorCodeException


@dataclass
class FightPreparationBehavior(Behavior):
    fight_movement_behavior: FightMovementBehavior
    fight_challenge_behavior: FightChallengeBehavior

    def run(self):
        self.fight_challenge_behavior.start(
            callback=self.on_fight_challenge_behavior_finished, parent=self
        )

    def on_fight_challenge_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        near_possible_cell_id = self.get_near_placement_cell_id()
        self.logger.info(f"found near cell id to enemy : {near_possible_cell_id}")
        if self.game_state.player.map_point.cell_id != near_possible_cell_id:
            self.logger.info(f"Moving to {near_possible_cell_id}")
            self.event_manager.on(
                EntitiesDispositionEvent,
                partial(
                    self.on_entity_disposition_event,
                    requested_cell_id=near_possible_cell_id,
                ),
                originator=self,
            )
            request = FightPlacementPositionRequest(
                cell_id=near_possible_cell_id,
                entity_id=self.game_state.player.character_id,
            )
            self.run_timer(ON_PLAYER_MOVED, lambda: self.event_manager.send(request))
        else:
            self.on_player_placement_done()

    def on_entity_disposition_event(
        self, msg: EntitiesDispositionEvent, requested_cell_id: int
    ):
        for disposition in msg.dispositions:
            if not disposition.cell_id == requested_cell_id:
                continue
            self.event_manager.clear_listener_by_origin_and_type(
                EntitiesDispositionEvent, self
            )
            return self.run_timer(ON_PLAYER_MOVED, self.on_player_placement_done)

    def on_player_placement_done(self):
        self.event_manager.on(
            FightStartEvent, lambda _: self.finish(), originator=self, once=True
        )
        request = FightReadyRequest(is_ready=True)
        self.run_timer(ON_CHALLENGE, lambda: self.event_manager.send(request))

    def get_near_placement_cell_id(self) -> int:
        min_dist_possible_cell_id: tuple[int, float] | None = None

        for (
            possible_cell_id
        ) in self.game_state.fight.fight_placement_possible_positions:
            mp_point_possible_cell = MapPoint.from_cell_id(possible_cell_id)
            near_enemy_with_dist = (
                self.fight_movement_behavior.find_near_enemy_with_dist(
                    mp_point_possible_cell
                )
            )
            if near_enemy_with_dist is None:
                continue
            cost_path = near_enemy_with_dist[2]
            if (
                min_dist_possible_cell_id is None
                or cost_path < min_dist_possible_cell_id[1]
            ):
                min_dist_possible_cell_id = (possible_cell_id, cost_path)

        if min_dist_possible_cell_id is None:
            raise ValueError(
                "There should be at least one possible placement position."
            )

        return min_dist_possible_cell_id[0]
