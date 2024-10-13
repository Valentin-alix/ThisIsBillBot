from dataclasses import dataclass
from functools import partial

from protos.game.context_pb2 import EntitiesDispositionEvent
from protos.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
    FightStartEvent,
    FightPlacementSwapPositionsOfferEvent,
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
        self.event_manager.on(
            FightStartEvent, lambda _: self.finish(), originator=self, once=True
        )
        self.fight_challenge_behavior.start(
            callback=self.on_fight_challenge_behavior_finished, parent=self
        )

    def on_fight_challenge_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            raise UnhandledErrorCodeException(error_code)

        self.position_player()

    def position_player(self):
        near_possible_cell_id = self.get_near_placement_cell_id()
        self.logger.info(f"found near cell id to enemy : {near_possible_cell_id}")
        if self.game_state.player.map_point.cell_id != near_possible_cell_id:
            self.logger.info(f"Moving to {near_possible_cell_id}")
            self.run_timer(
                (0.3, 0.6),
                partial(self.send_fight_placement_position, near_possible_cell_id),
            )
        else:
            self.on_player_placement_done()

    def send_fight_placement_position(self, cell_id: int):
        if self.game_state.entity.is_entity_actor_on_cell_id(cell_id):
            if cell_id == self.game_state.player.map_point.cell_id:
                return self.on_player_placement_done()
            self.logger.info("Cell id is occupied, try an other cell.")
            return self.position_player()

        self.event_manager.on(
            EntitiesDispositionEvent,
            partial(
                self.on_entity_disposition_event,
                requested_cell_id=cell_id,
            ),
            originator=self,
        )
        self.event_manager.on(
            FightPlacementSwapPositionsOfferEvent,
            callback=self.on_fight_placement_swap_positions_offer_event,
            originator=self,
        )
        request = FightPlacementPositionRequest(
            cell_id=cell_id,
            entity_id=self.game_state.player.character_id,
        )
        self.event_manager.send(request)

    def on_entity_disposition_event(
        self, msg: EntitiesDispositionEvent, requested_cell_id: int
    ):
        for disposition in msg.dispositions:
            if not disposition.cell_id == requested_cell_id:
                continue
            self.event_manager.clear_listener_by_origin_and_type(
                EntitiesDispositionEvent, self
            )
            self.event_manager.clear_listener_by_origin_and_type(
                FightPlacementSwapPositionsOfferEvent, self
            )
            if disposition.entity_id != self.game_state.player.character_id:
                return self.position_player()
            return self.run_timer(ON_PLAYER_MOVED, self.on_player_placement_done)

    def on_fight_placement_swap_positions_offer_event(
        self, msg: FightPlacementSwapPositionsOfferEvent
    ):
        if msg.requester_id != self.game_state.player.character_id:
            return
        self.logger.info("A player is already on this cell, take an other mp")
        self.event_manager.clear_listener_by_origin_and_type(
            EntitiesDispositionEvent, self
        )
        self.event_manager.clear_listener_by_origin_and_type(
            FightPlacementSwapPositionsOfferEvent, self
        )
        self.position_player()

    def on_player_placement_done(self):
        request = FightReadyRequest(is_ready=True)
        self.run_timer(ON_CHALLENGE, lambda: self.event_manager.send(request))

    def get_near_placement_cell_id(self) -> int:
        min_dist_possible_cell_id: tuple[int, float] | None = None

        for (
            possible_cell_id
        ) in self.game_state.fight.fight_placement_possible_positions:
            if (
                self.game_state.player.map_point.cell_id != possible_cell_id
                and self.game_state.entity.is_entity_actor_on_cell_id(possible_cell_id)
            ):
                continue
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
