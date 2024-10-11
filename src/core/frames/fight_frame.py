from dataclasses import dataclass

from protos.game.challenge_pb2 import ChallengeModSelectRequest
from protos.game.character_pb2 import CharacterCharacteristicsEvent
from protos.game.common_pb2 import Team
from protos.game.context_pb2 import (
    ContextCreationEvent,
)
from protos.game.fight_pb2 import (
    FightEndEvent,
    FightJoinRunningEvent,
    FightNewRoundEvent,
)
from protos.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
    FightStartingEvent,
    FightTeamUpdateEvent,
)
from protos.game.game_action_pb2 import GameActionFightEvent
from protos.game.gamemap_pb2 import FightMapInformationEvent
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
            once=True,
        )
        self.event_manager.on(
            FightMapInformationEvent,
            self.on_fight_map_information_event,
            originator=self,
        )

    def on_fight_placement_position_request(
        self, msg: FightPlacementPossiblePositionsEvent
    ):
        self.game_state.fight.fight_placement_possible_positions = (
            msg.starting_positions.challengers_positions
        )

    def on_context_creation_event(self, message: ContextCreationEvent):
        if message.context == ContextCreationEvent.GameContext.FIGHT:
            self.game_state.fight.in_fight = True

    def on_fight_end_event(self, message: FightEndEvent):
        self.game_state.fight.in_fight = False
        self.game_state.fight.is_map_fight_initialized = False

    def on_fight_starting_event(self, message: FightStartingEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        if message.attacker_id != self.game_state.player.character_id:
            self.game_state.fight.team = Team.TEAM_DEFENDER
        else:
            self.game_state.fight.team = Team.TEAM_CHALLENGER

    def on_spells_event(self, message: SpellsEvent):
        self.game_state.fight.spells = message.human_spells

    def on_spell_variant_activation_event(self, message: SpellVariantActivationEvent):
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
        self.game_state.fight.fight_turn = message.game_turn

    def on_fight_new_round_event(self, message: FightNewRoundEvent):
        self.game_state.fight.count_casted_by_target_by_spell_id.clear()
        self.game_state.fight.fight_turn = message.round_number

    def on_game_action_fight_event(self, message: GameActionFightEvent):
        if (
            message.HasField("targeted_ability")
            and message.source_id == self.game_state.player.character_id
            and message.targeted_ability.HasField("spell_cast")
        ):
            self.game_state.fight.count_casted_by_target_by_spell_id[
                message.targeted_ability.spell_cast.spell_id
            ][message.targeted_ability.target_id] += 1

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
        del self.game_state.fight.modifier_by_type_and_spell_id[
            (message.spell_id, message.modifier_type)
        ]

    def on_character_characteristics_event(
        self, message: CharacterCharacteristicsEvent
    ):
        self.game_state.fight.modifier_by_type_and_spell_id.clear()
        for spell_modifier in message.stats.spell_modifiers:
            self.game_state.fight.modifier_by_type_and_spell_id[
                (spell_modifier.spell_id, spell_modifier.modifier_type)
            ] = spell_modifier

    def on_fight_team_update_event(self, message: FightTeamUpdateEvent):
        if message.team.team == self.game_state.fight.team:
            self.game_state.fight.leader_id = message.team.leader_id

    def on_challenge_mod_select_request(self, msg: ChallengeModSelectRequest):
        self.game_state.fight.challenge_mod = msg.challenge_mod

    def on_fight_map_information_event(self, msg: FightMapInformationEvent):
        self.game_state.fight.is_map_fight_initialized = True
