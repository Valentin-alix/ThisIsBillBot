from dataclasses import dataclass

from d3_mapping.resources.protos.game.challenge_pb2 import ChallengeModSelectRequest
from d3_mapping.resources.protos.game.character_pb2 import CharacterCharacteristicsEvent
from d3_mapping.resources.protos.game.context_pb2 import (
    ContextCreationEvent,
)
from d3_mapping.resources.protos.game.fight_pb2 import (
    FightEndEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
    FightTurnEndEvent,
    FightIsTurnReadyEvent,
    FightTurnStartPlayingEvent,
    FightTurnEvent,
)
from d3_mapping.resources.protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
)
from d3_mapping.resources.protos.game.game_action_pb2 import GameActionFightEvent
from d3_mapping.resources.protos.game.spell_pb2 import (
    SpellsEvent,
)
from src.core.frames.frame import Frame


@dataclass
class FightFrame(Frame):
    def __post_init__(self):
        self.game_info_signals.disconnected.connect(self.game_state.fight.clear_state)
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
        self.event_manager.on(SpellsEvent, self.on_spells_event, originator=self)
        self.event_manager.on(
            GameActionFightEvent, self.on_game_action_fight_event, originator=self
        )
        self.event_manager.on(
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
        )
        self.event_manager.on(
            ChallengeModSelectRequest,
            self.on_challenge_mod_select_request,
            originator=self,
        )
        self.event_manager.before(
            FightTurnFinishRequest,
            self.before_fight_turn_finish_request,
            originator=self,
        )
        self.event_manager.before(
            FightTurnReadyRequest, self.before_fight_turn_ready_request, originator=self
        )
        self.event_manager.on(
            FightTurnEndEvent, self.on_fight_turn_end_event, originator=self
        )
        self.event_manager.on(
            FightIsTurnReadyEvent, self.on_fight_is_turn_ready_event, originator=self
        )
        self.event_manager.on(FightTurnEvent, self.on_fight_turn_event, originator=self)

    def on_fight_placement_position_request(
        self, msg: FightPlacementPossiblePositionsEvent
    ):
        self.game_state.fight.fight_placement_possible_positions = list(
            msg.starting_positions.challengers_positions
        )

    def on_context_creation_event(self, message: ContextCreationEvent):
        if message.context == ContextCreationEvent.GameContext.FIGHT:
            self.game_state.fight.in_fight = True
        else:
            self.game_state.fight.in_fight = False

    def on_fight_end_event(self, message: FightEndEvent):
        self.game_state.fight.in_fight = False
        self.game_state.fight.is_map_fight_initialized = False

    def on_fight_starting_event(self, message: FightStartingEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.last_triggered_turn_by_spell_id.clear()
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        self.game_state.fight.fight_placement_possible_positions.clear()

    def on_spells_event(self, message: SpellsEvent):
        self.game_state.fight.spells = list(message.human_spells)

    def on_game_action_fight_event(self, message: GameActionFightEvent):
        if message.HasField("targeted_ability") and message.targeted_ability.HasField(
            "spell_cast"
        ):
            if message.source_id == self.game_state.player.character_id:
                self.game_state.fight.count_casted_by_target_by_spell_id[
                    message.targeted_ability.spell_cast.spell_id
                ][message.targeted_ability.target_id] += 1

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        for spell_modifier in message.stats.spell_modifiers:
            self.game_state.fight.modifier_by_type_and_spell_id[
                (spell_modifier.spell_id, spell_modifier.modifier_type)
            ] = spell_modifier

    def on_challenge_mod_select_request(self, msg: ChallengeModSelectRequest):
        self.game_state.fight.challenge_mod = msg.challenge_mod

    def before_fight_turn_finish_request(
        self, msg: FightTurnFinishRequest
    ) -> FightTurnFinishRequest | None:
        if self.is_playing_event.is_set() and msg.is_active is False:
            return None
        return msg

    def before_fight_turn_ready_request(self, msg: FightTurnReadyRequest):
        if self.is_playing_event.is_set():
            return None
        return msg

    def on_fight_turn_start_playing_event(self, msg: FightTurnStartPlayingEvent):
        self.game_state.fight.is_our_turn = True

    def on_fight_turn_end_event(self, msg: FightTurnEndEvent):
        self.game_state.fight.is_our_turn = False

    def on_fight_is_turn_ready_event(self, msg: FightIsTurnReadyEvent):
        self.game_state.fight.is_our_turn = False

    def on_fight_turn_event(self, msg: FightTurnEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.is_our_turn = True
