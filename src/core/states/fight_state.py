import dataclasses
from collections import defaultdict
from dataclasses import dataclass, field

from d3_mapping.resources.protos.game.common_pb2 import (
    SpellModifier,
    SpellModifierType,
    ChallengeMod,
)
from d3_mapping.resources.protos.game.spell_pb2 import SpellItem
from src.core.logic.fight.effect import get_effect_elem_by_stat
from src.core.states.player_state import PlayerState
from src.core.states.state import State
from src.interfaces.enums.characteristic_enum import CharacteristicEnum
from src.interfaces.enums.effect_element import EffectElement
from src.signals.player_signals import GameInfoSignals


@dataclass
class FightState(State):
    player_state: PlayerState
    game_info_signals: GameInfoSignals

    is_map_fight_initialized: bool = field(init=False, default=False)
    fight_placement_possible_positions: list[int] = field(
        default_factory=list, init=False
    )
    is_our_turn: bool = field(default=False, init=False)
    challenge_mod: ChallengeMod = field(
        init=False, default=ChallengeMod.CHALLENGE_CHOICE
    )
    spells: list[SpellItem] = dataclasses.field(init=False, default_factory=list)
    modifier_by_type_and_spell_id: dict[
        tuple[int, SpellModifierType], SpellModifier
    ] = dataclasses.field(init=False, default_factory=dict)
    count_casted_by_target_by_spell_id: dict[int, dict[int, int]] = dataclasses.field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int)), init=False
    )
    last_triggered_turn_by_spell_id: dict[int, int] = dataclasses.field(
        default_factory=dict, init=False
    )
    _in_fight: bool = dataclasses.field(init=False, default=False)
    _fight_turn: int = dataclasses.field(init=False, default=0)

    def clear_state(self):
        self.is_map_fight_initialized = False
        self.fight_placement_possible_positions.clear()
        self.is_our_turn = False
        self.challenge_mod = ChallengeMod.CHALLENGE_CHOICE
        self.spells.clear()
        self.modifier_by_type_and_spell_id.clear()
        self.count_casted_by_target_by_spell_id.clear()
        self.last_triggered_turn_by_spell_id.clear()
        self.in_fight = False

    @property
    def in_fight(self):
        return self._in_fight

    @in_fight.setter
    def in_fight(self, value: bool):
        self._in_fight = value
        self.game_info_signals.in_fight.emit(self._in_fight)

    @property
    def ordered_stat(self) -> list[CharacteristicEnum]:
        dmg_stats = [
            CharacteristicEnum.AGILITY,
            CharacteristicEnum.STRENGTH,
            CharacteristicEnum.INTELLIGENCE,
            CharacteristicEnum.CHANCE,
        ]
        return list(
            sorted(dmg_stats, key=self.player_state.get_player_stat_by_id, reverse=True)
        )

    @property
    def primary_and_second_elem(self) -> tuple[EffectElement, EffectElement]:
        ordered_stats = self.ordered_stat
        return (
            get_effect_elem_by_stat(ordered_stats[0]),
            get_effect_elem_by_stat(ordered_stats[1]),
        )
