from dataclasses import dataclass
from functools import partial

from db_dofus_unity.protos.game.fight_pb2 import FightTurnFinishRequest
from db_dofus_unity.protos.game.game_action_pb2 import (
    GameActionAcknowledgementRequest,
    SequenceEndEvent,
    SequenceType,
)
from db_dofus_unity.protos.game.gamemap_pb2 import MapComplementaryInformationEvent
from src.consts import BASE_RANGE, SMALL_RANGE, VERY_SMALL_RANGE
from src.core.behaviors.behavior import Behavior
from src.core.behaviors.fight.fight_movement_behavior import FightMovementBehavior
from src.core.behaviors.fight.fight_placement_behavior import FightPlacementBehavior
from src.core.behaviors.fight.fight_spell_behavior import FightSpellBehavior
from src.core.behaviors.movements.map_move_behavior import MapMoveBehavior
from src.core.logic.grid.path_finding.path_finding import Pathfinding
from src.core.states.entity_state import EntityState
from src.core.states.fight_state import FightState
from src.core.states.map_state import MapState
from src.core.states.player_state import PlayerState
from src.interfaces.enums.action_id import ActionId


@dataclass
class FightBehavior(Behavior):
    player_state: PlayerState
    fight_state: FightState
    map_state: MapState
    entity_state: EntityState
    path_finding: Pathfinding
    fight_movement_behavior: FightMovementBehavior
    fight_spell_behavior: FightSpellBehavior
    map_move_behavior: MapMoveBehavior
    fight_placement_behavior: FightPlacementBehavior

    def run(self):
        self.event_manager.on(
            MapComplementaryInformationEvent,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        self.run_timer(
            BASE_RANGE,
            lambda: self.fight_placement_behavior.start(
                callback=self.on_fight_placement_behavior_finish, parent=self
            ),
        )

    def on_fight_placement_behavior_finish(self, error_code: str | None):
        if error_code is not None:
            return
        self.event_manager.on(
            SequenceEndEvent,
            self.on_sequence_end_event,
            originator=self,
        )

    def on_sequence_end_event(self, msg: SequenceEndEvent):
        if (
            msg.author_id == self.player_state.character_id
            and msg.sequence_type == SequenceType.TRIGGERED
            and msg.action_id == ActionId.TURN
        ):
            self.event_manager.on(
                GameActionAcknowledgementRequest,
                partial(
                    self.on_game_action_acknowledgement_request,
                    target_action_id=msg.action_id,
                ),
                originator=self,
            )

    def on_game_action_acknowledgement_request(
        self, msg: GameActionAcknowledgementRequest, target_action_id: int
    ):
        if msg.action_id == target_action_id:
            self.event_manager.clear_listener_by_origin_and_type(
                GameActionAcknowledgementRequest, self
            )
            self.on_player_turn()

    def on_player_turn(self):
        self.run_timer(
            SMALL_RANGE,
            lambda: self.fight_movement_behavior.start(
                callback=self.on_fight_movement_behavior_finish,
                parent=self,
            ),
        )

    def on_fight_movement_behavior_finish(self, error_code: str):
        if error_code is not None:
            return
        self.run_timer(
            SMALL_RANGE,
            lambda: self.fight_spell_behavior.start(
                callback=self.on_fight_spell_behavior_finish, parent=self
            ),
        )

    def on_fight_spell_behavior_finish(self, error_code: str):
        if error_code is not None:
            return
        self.run_timer(VERY_SMALL_RANGE, self.pass_turn)

    def pass_turn(self):
        req = FightTurnFinishRequest()
        self.event_manager.send(req)
