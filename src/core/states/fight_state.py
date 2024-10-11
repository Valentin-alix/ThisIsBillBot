import dataclasses
from collections import defaultdict
from dataclasses import dataclass, field

from protos.game.common_pb2 import (
    Team,
    SpellItem,
    SpellModifier,
    SpellModifierType,
    ChallengeMod,
)
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
    leader_id: int = field(default=0, init=False)
    fight_placement_possible_positions: list[int] = field(
        default_factory=list, init=False
    )
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
    state_ids: set[int] = dataclasses.field(init=False, default_factory=set)
    _in_fight: bool = dataclasses.field(init=False, default=False)
    _team: Team = dataclasses.field(init=False, default=Team.TEAM_NEUTRAL)
    _fight_turn: int = dataclasses.field(init=False, default=0)

    @property
    def team(self):
        return self._team

    @team.setter
    def team(self, value: Team):
        self._team = value
        self.game_info_signals.team.emit(self._team)

    @property
    def fight_turn(self):
        return self._fight_turn

    @fight_turn.setter
    def fight_turn(self, value: int):
        self._fight_turn = value
        self.game_info_signals.team.emit(self._fight_turn)

    @property
    def in_fight(self):
        return self._in_fight

    @in_fight.setter
    def in_fight(self, value: bool):
        self._in_fight = value
        self.game_info_signals.in_fight.emit(self._in_fight)

    @property
    def primary_stat(self) -> int:
        dmg_stats = [
            CharacteristicEnum.AGILITY,
            CharacteristicEnum.STRENGTH,
            CharacteristicEnum.INTELLIGENCE,
            CharacteristicEnum.CHANCE,
        ]
        return max(dmg_stats, key=self.player_state.get_stat_by_id)

    @property
    def primary_elem(self) -> EffectElement:
        primary_stat = self.primary_stat
        match primary_stat:
            case CharacteristicEnum.CHANCE:
                return EffectElement.CHANCE
            case CharacteristicEnum.STRENGTH:
                return EffectElement.STRENGTH
            case CharacteristicEnum.INTELLIGENCE:
                return EffectElement.INTELLIGENCE
            case CharacteristicEnum.AGILITY:
                return EffectElement.AGILITY
            case _:
                raise ValueError(f"Unknown primary stat : {primary_stat} for elem")
