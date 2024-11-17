import dataclasses
from collections import defaultdict
from dataclasses import dataclass, field

from D3Database.enums.characteristic_enum import CharacteristicEnum
from D3Database.enums.effect_element import EffectElement
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    SpellModifier,
    SpellModifierType,
)
from D3Mapping.d3_mapping.resources.protos.game.spell_pb2 import SpellItem
from src.core.engine.fights.effect import get_effect_elem_by_stat
from src.core.engine.fights.stats.characteristic import get_stat_by_id
from src.core.signals.player_signals import GameInfoSignals
from src.core.states.entity_state import EntityState
from src.core.states.player_state import PlayerState
from src.core.states.state import State


@dataclass
class FightState(State):
    player_state: PlayerState
    entity_state: EntityState
    game_info_signals: GameInfoSignals

    is_map_fight_initialized: bool = field(init=False, default=False)
    fight_placement_possible_positions: list[int] = field(
        default_factory=list, init=False
    )
    _is_our_turn: bool = field(default=False, init=False)
    spells: list[SpellItem] = dataclasses.field(init=False, default_factory=list)
    modifier_by_type_and_spell_id: dict[
        tuple[int, SpellModifierType], SpellModifier
    ] = dataclasses.field(init=False, default_factory=dict)
    count_casted_by_spell_id_on_current_turn: dict[int, int] = dataclasses.field(
        default_factory=lambda: defaultdict(int), init=False
    )
    characteristic_by_id: dict[int, CharacterCharacteristic] = dataclasses.field(
        init=False, default_factory=dict
    )
    _breed_id: int = dataclasses.field(init=False, default=0)
    _in_fight: bool = dataclasses.field(init=False, default=False)
    _fight_turn: int = dataclasses.field(init=False, default=0)
    _life_point: int = dataclasses.field(init=False, default=1)
    _max_life_point: int = dataclasses.field(init=False, default=1)
    _last_attacked_monster_group: (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor | None
    ) = dataclasses.field(init=False, default=None)
    _player_died_in_current_fight: bool = dataclasses.field(init=False, default=False)

    def clear_state(self):
        self.is_map_fight_initialized = False
        self.fight_placement_possible_positions.clear()
        self.is_our_turn = False
        self.spells.clear()
        self.modifier_by_type_and_spell_id.clear()
        self.count_casted_by_spell_id_on_current_turn.clear()
        self.characteristic_by_id.clear()
        self.breed_id = 0
        self.in_fight = False
        self.fight_turn = 0
        self.life_point = 1
        self.max_life_point = 1
        self._last_attacked_monster_group = None
        self._player_died_in_current_fight = False

    def get_stat_by_id(self, characteristic: int) -> int:
        value = get_stat_by_id(self.characteristic_by_id.get(characteristic))
        return value

    def update_characteristic(self, characteristic: CharacterCharacteristic) -> None:
        self.characteristic_by_id[characteristic.characteristic_id] = characteristic

    @property
    def breed_id(self):
        return self._breed_id

    @breed_id.setter
    def breed_id(self, value: int):
        self._breed_id = value
        self.game_info_signals.breed_id.emit(value)

    @property
    def max_life_point(self):
        return max(self._max_life_point, 1)

    @max_life_point.setter
    def max_life_point(self, value: int):
        self.game_info_signals.max_life_point.emit(value)
        self._max_life_point = value

    @property
    def life_percentage(self):
        return self.life_point / self.max_life_point

    @property
    def fight_turn(self):
        return self._fight_turn

    @fight_turn.setter
    def fight_turn(self, value: int):
        self.game_info_signals.fight_turn.emit(value)
        self._fight_turn = value

    @property
    def life_point(self):
        return max(self._life_point, 1)

    @life_point.setter
    def life_point(self, value: int):
        self.game_info_signals.life_point.emit(value)
        self._life_point = value

    @property
    def in_fight(self):
        return self._in_fight

    @in_fight.setter
    def in_fight(self, value: bool):
        self._in_fight = value
        self.game_info_signals.in_fight.emit(self._in_fight)

    @property
    def ordered_stat(self) -> list[int]:
        dmg_stats: list[CharacteristicEnum] = [
            CharacteristicEnum.AGILITY,
            CharacteristicEnum.STRENGTH,
            CharacteristicEnum.INTELLIGENCE,
            CharacteristicEnum.CHANCE,
        ]
        return list(sorted(dmg_stats, key=self.get_stat_by_id, reverse=True))

    @property
    def primary_and_second_elem(self) -> tuple[EffectElement, EffectElement]:
        ordered_stats = self.ordered_stat
        return (
            get_effect_elem_by_stat(ordered_stats[0]),
            get_effect_elem_by_stat(ordered_stats[1]),
        )

    @property
    def is_our_turn(self) -> bool:
        return self._is_our_turn

    @is_our_turn.setter
    def is_our_turn(self, value: bool):
        self._is_our_turn = value
        self.game_info_signals.is_our_turn.emit(value)

    def get_enemies(self, character_id: int) -> list[ActorPositionInformation]:
        enemies = [
            actor
            for actor in self.entity_state.actor_by_id.values()
            if actor.actor_id != character_id and actor.disposition.cell_id != -1
            # and actor.actor_id in self.actor_fight_by_id
        ]
        self.logger.info(f"Found {len(enemies)} enemies")

        return enemies

    def set_last_attacked_monster_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor
        | None,
    ):
        self._last_attacked_monster_group = monster_group

    @property
    def last_attacked_monster_group(
        self,
    ) -> (
        ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor | None
    ):
        return self._last_attacked_monster_group

    def set_player_died_in_current_fight(self, died: bool):
        self._player_died_in_current_fight = died

    @property
    def player_died_in_current_fight(self) -> bool:
        return self._player_died_in_current_fight
