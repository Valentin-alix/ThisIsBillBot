from dataclasses import dataclass

from protos.game.challenge_pb2 import ChallengeModSelectRequest
from protos.game.character_pb2 import CharacterCharacteristicsEvent
from protos.game.context_pb2 import (
    ContextCreationEvent,
)
from protos.game.fight_pb2 import (
    FightEndEvent,
    FightJoinRunningEvent,
    FightNewRoundEvent,
    FightTurnFinishRequest,
    FightTurnReadyRequest,
    FightFighterShowEvent,
    FightTurnEndEvent,
    FightIsTurnReadyEvent,
    FightTurnStartPlayingEvent,
    FightTurnEvent,
)
from protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
    FightTeamUpdateEvent,
)
from protos.game.game_action_pb2 import GameActionFightEvent
from protos.game.spell_pb2 import (
    SpellsEvent,
    SpellVariantActivationEvent,
    SpellItem,
    ApplySpellModifierEvent,
    RemoveSpellModifierEvent,
)
from src.core.data_center.data_reader import DataReader
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
            SpellVariantActivationEvent,
            self.on_spell_variant_activation_event,
            originator=self,
        )
        self.event_manager.on(
            FightJoinRunningEvent, self.on_fight_join_running_event, originator=self
        )
        self.event_manager.on(
            FightNewRoundEvent, self.on_fight_new_round_event, originator=self
        )
        self.event_manager.on(
            GameActionFightEvent, self.on_game_action_fight_event, originator=self
        )
        self.event_manager.on(
            ApplySpellModifierEvent, self.on_apply_spell_modifier_event, originator=self
        )
        self.event_manager.on(
            RemoveSpellModifierEvent,
            self.on_remove_spell_modifier_event,
            originator=self,
        )
        self.event_manager.on(
            CharacterCharacteristicsEvent,
            self.on_character_characteristics_event,
            originator=self,
        )
        self.event_manager.on(
            FightTeamUpdateEvent, self.on_fight_team_update_event, originator=self
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
            FightFighterShowEvent, self.on_fight_fighter_show_event, originator=self
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

    def on_spell_variant_activation_event(self, message: SpellVariantActivationEvent):
        if message.spell_id == 0:
            return
        opposite_spell_id = DataReader().spell_opposite_variant_by_spell_id[
            message.spell_id
        ]
        self.game_state.fight.spells = [
            spell
            for spell in self.game_state.fight.spells
            if spell.spell_id != opposite_spell_id
        ]
        self.game_state.fight.spells.append(
            SpellItem(spell_id=message.spell_id, spell_level=1)
        )

    def on_fight_join_running_event(self, message: FightJoinRunningEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.last_triggered_turn_by_spell_id.clear()
        self.game_state.fight.fight_turn = message.game_turn

    def on_fight_new_round_event(self, message: FightNewRoundEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.fight_turn = message.round_number

    def on_game_action_fight_event(self, message: GameActionFightEvent):
        if message.HasField("targeted_ability") and message.targeted_ability.HasField(
            "spell_cast"
        ):
            if message.source_id == self.game_state.player.character_id:
                self.game_state.fight.count_casted_by_target_by_spell_id[
                    message.targeted_ability.spell_cast.spell_id
                ][message.targeted_ability.target_id] += 1
            self.game_state.fight.last_triggered_turn_by_spell_id[
                message.targeted_ability.spell_cast.spell_id
            ] = self.game_state.fight.fight_turn

        if message.HasField("removable_effect"):
            effect = message.removable_effect.effect
            if effect.target_id == self.game_state.player.character_id:
                if effect.HasField("temporary_boost_effect"):
                    self.game_state.fight.state_ids.add(
                        effect.temporary_boost_effect.state_id
                    )

    def on_apply_spell_modifier_event(self, message: ApplySpellModifierEvent):
        self.game_state.fight.modifier_by_type_and_spell_id[
            (message.modifier.spell_id, message.modifier.modifier_type)
        ] = message.modifier

    def on_remove_spell_modifier_event(self, message: RemoveSpellModifierEvent):
        self.game_state.fight.modifier_by_type_and_spell_id.pop(
            (message.spell_id, message.modifier_type), None
        )

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        for spell_modifier in message.stats.spell_modifiers:
            self.game_state.fight.modifier_by_type_and_spell_id[
                (spell_modifier.spell_id, spell_modifier.modifier_type)
            ] = spell_modifier

    def on_fight_team_update_event(self, message: FightTeamUpdateEvent):
        if message.team.leader_id == self.game_state.player.character_id:
            self.game_state.fight.team = message.team.team
            self.game_state.fight.leader_id = message.team.leader_id
            return
        for team_member in message.team.team_members.team_members:
            if team_member.member_id == self.game_state.player.character_id:
                self.game_state.fight.team = message.team.team
                self.game_state.fight.leader_id = message.team.leader_id
                break

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

    def on_fight_fighter_show_event(self, msg: FightFighterShowEvent):
        if msg.information.actor_id == self.game_state.player.character_id:
            self.game_state.fight.team = (
                msg.information.actor_information.fighter.spawn_information.team
            )

    def on_fight_turn_start_playing_event(self, msg: FightTurnStartPlayingEvent):
        self.game_state.fight.is_our_turn = True

    def on_fight_turn_end_event(self, msg: FightTurnEndEvent):
        self.game_state.fight.is_our_turn = False

    def on_fight_is_turn_ready_event(self, msg: FightIsTurnReadyEvent):
        self.game_state.fight.is_our_turn = False

    def on_fight_turn_event(self, msg: FightTurnEvent):
        self.game_state.fight.is_our_turn = True
