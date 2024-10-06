from dataclasses import dataclass

from db_dofus_unity.protos.game.common_pb2 import Team
from db_dofus_unity.protos.game.context_pb2 import (
    ContextCreationEvent,
)
from db_dofus_unity.protos.game.fight_pb2 import (
    FightEndEvent,
)
from db_dofus_unity.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
)
from src.core.frames.frame import Frame
from src.core.states.fight_state import FightState
from src.core.states.player_state import PlayerState


@dataclass
class FightFrame(Frame):
    player_state: PlayerState
    fight_state: FightState

    def __post_init__(self):
        self.event_manager.on(
            FightPlacementPossiblePositionsEvent,
            self.on_fight_placement_position_request,
            originator=self,
        )
        self.event_manager.on(
            ContextCreationEvent,
            self.on_context_creation_event,
            originator=self,
        )
        self.event_manager.on(
            FightEndEvent,
            self.on_fight_end_event,
            originator=self,
        )
        self.event_manager.on(
            FightStartingEvent, self.on_fight_starting_event, originator=self
        )

    def on_fight_placement_position_request(
        self, msg: FightPlacementPossiblePositionsEvent
    ):
        self.fight_state.fight_placement_possible_positions = (
            msg.starting_positions.challengers_positions
        )

    def on_context_creation_event(self, message: ContextCreationEvent):
        if message.context == ContextCreationEvent.GameContext.FIGHT:
            self.fight_state.in_fight = True

    def on_fight_end_event(self, message: FightEndEvent):
        self.fight_state.in_fight = False

    def on_fight_starting_event(self, message: FightStartingEvent):
        if message.attacker_id != self.player_state.character_id:
            self.fight_state.team = Team.TEAM_DEFENDER
        else:
            self.fight_state.team = Team.TEAM_CHALLENGER
