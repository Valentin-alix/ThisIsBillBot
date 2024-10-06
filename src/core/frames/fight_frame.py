from dataclasses import dataclass

from db_dofus_unity.protos.game.context_pb2 import (
    ContextCreationEvent,
    EntitiesDispositionEvent,
)
from db_dofus_unity.protos.game.fight_pb2 import (
    FightEndEvent,
    FightSynchronizeEvent,
    FightFighterShowEvent,
    FightFighterRefreshEvent,
)
from db_dofus_unity.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
)
from db_dofus_unity.protos.game.game_action_pb2 import GameActionFightEvent
from db_dofus_unity.protos.game.gamemap_pb2 import MapMovementEvent
from src.core.frames.frame import Frame
from src.core.states.fight_state import FightState


@dataclass
class FightFrame(Frame):
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
            FightSynchronizeEvent, self.on_fight_synchronize_event, originator=self
        )
        self.event_manager.on(
            FightFighterShowEvent, self.on_fight_fighter_show_event, originator=self
        )
        self.event_manager.on(
            FightFighterRefreshEvent,
            self.on_fight_fighter_refresh_event,
            originator=self,
        )
        self.event_manager.on(
            MapMovementEvent, self.on_map_movement_event, originator=self
        )
        self.event_manager.on(
            EntitiesDispositionEvent,
            self.on_entities_disposition_event,
            originator=self,
        )
        self.event_manager.on(
            GameActionFightEvent, self.on_game_action_fight_event, originator=self
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

    def on_fight_synchronize_event(self, msg: FightSynchronizeEvent):
        self.fight_state.actor_by_id = {actor.actor_id: actor for actor in msg.fighters}

    def on_fight_fighter_show_event(self, msg: FightFighterShowEvent):
        self.fight_state.actor_by_id[msg.information.actor_id] = msg.information

    def on_fight_fighter_refresh_event(self, msg: FightFighterRefreshEvent):
        self.fight_state.actor_by_id[msg.information.actor_id] = msg.information

    def on_map_movement_event(self, msg: MapMovementEvent):
        if not self.fight_state.in_fight:
            return
        if len(msg.cells) > 0:
            self.fight_state.actor_by_id[msg.character_id].disposition.cell_id = (
                msg.cells[-1]
            )
        self.fight_state.actor_by_id[msg.character_id].disposition.direction = (
            msg.direction
        )

    def on_entities_disposition_event(self, msg: EntitiesDispositionEvent):
        for disposition in msg.dispositions:
            if disposition.entity_id not in self.fight_state.actor_by_id:
                continue
            self.fight_state.actor_by_id[disposition.entity_id].disposition.cell_id = (
                disposition.cell_id
            )
            self.fight_state.actor_by_id[
                disposition.entity_id
            ].disposition.direction = disposition.direction

    def on_game_action_fight_event(self, msg: GameActionFightEvent):
        if msg.HasField("death"):
            self.fight_state.actor_by_id.pop(msg.death.target_id)
