import random
from dataclasses import dataclass, field
from functools import partial

from DBDofusUnity.datas.protos.non_obf.game.context_pb2 import EntitiesDispositionEvent
from DBDofusUnity.datas.protos.non_obf.game.fight_preparation_pb2 import (
    FightPlacementPositionRequest,
    FightReadyRequest,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.farms.fight.fight_movement_behavior import FightMovementBehavior
from src.core.config import (
    PLACEMENT_NON_OPTIMAL_MOVE_PROBABILITY,
    PLACEMENT_REPOSITIONING_PROBABILITY,
)
from src.services.human_timings import HumanTimingsService


@dataclass
class FightPreparationBehavior(Behavior):
    fight_movement_behavior: FightMovementBehavior

    _has_repositioned: bool = field(init=False, default=False)
    _has_done_non_optimal_move: bool = field(init=False, default=False)
    _should_do_non_optimal_move: bool = field(init=False, default=False)
    _has_returned_to_optimal: bool = field(init=False, default=False)

    def run(self) -> None:
        self._has_repositioned = False
        self._has_done_non_optimal_move = False
        self._has_returned_to_optimal = False
        self._should_do_non_optimal_move = random.random() < PLACEMENT_NON_OPTIMAL_MOVE_PROBABILITY
        self.event_manager.on(FightReadyRequest, lambda _: self.finish(), originator=self, once=True)
        self.position_player()

    def position_player(self) -> None:
        near_possible_cell_id = self.get_near_placement_cell_id()
        self.logger.info(f"found near cell id to enemy : {near_possible_cell_id}")

        if self._should_do_non_optimal_move and not self._has_done_non_optimal_move:
            non_optimal_cell = self.get_random_non_optimal_cell(near_possible_cell_id)
            if non_optimal_cell is not None:
                self._has_done_non_optimal_move = True
                self.logger.debug(f"Moving to non-optimal cell {non_optimal_cell} before optimal")
                self.send_fight_placement_position(non_optimal_cell)
                return

        if self.game_state.map.map_point.cell_id != near_possible_cell_id:
            self.logger.info(f"Moving to {near_possible_cell_id}")
            self.send_fight_placement_position(near_possible_cell_id)
        else:
            self.on_player_placement_done()

    def send_fight_placement_position(self, cell_id: int) -> None:
        if self.game_state.entity.actors_on_mp.is_entity_actor_on_cell_id(cell_id):
            if cell_id == self.game_state.map.map_point.cell_id:
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
        request = FightPlacementPositionRequest(
            cell_id=cell_id,
            entity_id=self.game_state.player.character_id,
        )
        self.send_message_delayed(request, HumanTimingsService().get_timing_before_preparation_placement())

    def on_entity_disposition_event(self, msg: EntitiesDispositionEvent, requested_cell_id: int) -> None:
        for disposition in msg.dispositions:
            if disposition.cell_id != requested_cell_id:
                continue
            self.unregister_listener(
                EntitiesDispositionEvent,
                reason="Received entity disposition for requested cell",
            )
            if self.game_state.player.character_id not in [
                disposition.entity_id,
                disposition.carrying_character_id,
            ]:
                return self.position_player()

            self.on_player_placement_done()

    def on_player_placement_done(self) -> None:
        if self._has_done_non_optimal_move and not self._has_returned_to_optimal:
            self._has_returned_to_optimal = True
            self.logger.debug("Feint done, returning to optimal cell")
            return self.run_timer(
                HumanTimingsService().get_timing_placement_extra_hesitation(),
                self.position_player,
            )

        if not self._has_repositioned and random.random() < PLACEMENT_REPOSITIONING_PROBABILITY:
            self._has_repositioned = True
            self.logger.debug("Hesitating, repositioning...")
            return self.run_timer(
                HumanTimingsService().get_timing_placement_extra_hesitation(),
                self.position_player,
            )

        request = FightReadyRequest(is_ready=True)
        self.send_message_delayed(request, HumanTimingsService().get_timing_before_preparation_ready())

    def get_near_placement_cell_id(self) -> int:
        min_dist_possible_cell_id: tuple[int, float] | None = None

        for possible_cell_id in self.game_state.fight.fight_placement_possible_positions:
            if (
                self.game_state.map.map_point.cell_id != possible_cell_id
                and self.game_state.entity.actors_on_mp.is_entity_actor_on_cell_id(possible_cell_id)
            ):
                continue
            mp_point_possible_cell = MapPoint.from_cell_id(possible_cell_id)
            near_enemy_with_dist = self.fight_movement_behavior.find_near_enemy_with_dist(
                mp_point_possible_cell
            )
            if near_enemy_with_dist is None:
                continue
            cost_path = near_enemy_with_dist[2]
            if min_dist_possible_cell_id is None or cost_path < min_dist_possible_cell_id[1]:
                min_dist_possible_cell_id = (possible_cell_id, cost_path)

        if min_dist_possible_cell_id is None:
            raise ValueError("There should be at least one possible placement position.")

        return min_dist_possible_cell_id[0]

    def get_random_non_optimal_cell(self, optimal_cell_id: int) -> int | None:
        non_optimal_cells: list[int] = []
        for cell_id in self.game_state.fight.fight_placement_possible_positions:
            if cell_id == optimal_cell_id:
                continue
            if cell_id == self.game_state.map.map_point.cell_id:
                continue
            if self.game_state.entity.actors_on_mp.is_entity_actor_on_cell_id(cell_id):
                continue
            non_optimal_cells.append(cell_id)

        if not non_optimal_cells:
            return None
        return random.choice(non_optimal_cells)
