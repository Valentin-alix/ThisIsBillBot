from dofus_unity_reader.enums.characteristic_enum import CharacteristicEnum
from datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicsEvent,
    UpdateLifePointsEvent,
)
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    CharacterCharacteristics,
    CharacterCharacteristicValue,
    EntityDisposition,
    FightStartingPositions,
    SpellModifier,
    SpellModifierType,
)
from datas.protos.non_obf.game.fight_pb2 import (
    FightTurnFinishRequest,
    FightTurnStartPlayingEvent,
)
from datas.protos.non_obf.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionFightCastRequest,
    GameActionFightEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapComplementaryInformationEvent,
)
from datas.protos.non_obf.game.spell_pb2 import SpellItem, SpellsEvent
from tests.test_states.state_test_base import StateTestBase


class TestFightState(StateTestBase):
    def test_fight_starting_clears_counters(self):
        self.game_state.fight.count_casted_by_spell_id_on_current_turn[123] = 5
        self.game_state.fight.modifier_by_type_and_spell_id[
            (1, SpellModifierType.RANGE)
        ] = SpellModifier()
        self.game_state.fight.fight_placement_possible_positions = [100, 200]

        self.inject(FightMapInformationEvent())
        self.inject(FightTurnStartPlayingEvent())

        assert len(self.game_state.fight.count_casted_by_spell_id_on_current_turn) == 0
        assert len(self.game_state.fight.modifier_by_type_and_spell_id) == 0

    def test_spells_event_sets_spells(self):
        spells = [
            SpellItem(spell_id=100, spell_level=1, available=True),
            SpellItem(spell_id=200, spell_level=2, available=True),
        ]
        msg = SpellsEvent(human_spells=spells)

        self.inject(msg)

        assert len(self.game_state.fight.spells) == 2
        assert self.game_state.fight.spells[0].spell_id == 100
        assert self.game_state.fight.spells[1].spell_id == 200

    def test_fight_turn_start_playing_sets_our_turn_and_increments(self):
        self.game_state.fight.is_our_turn = False
        self.game_state.fight.fight_turn = 0

        self.inject(FightTurnStartPlayingEvent())

        assert self.game_state.fight.is_our_turn is True
        assert self.game_state.fight.fight_turn == 1

    def test_fight_placement_positions_for_challenger(self):
        # Setup: create player actor at cell 100 (in challengers)
        self.game_state.player.character_id = 1
        actor = ActorPositionInformation(
            actor_id=1, disposition=EntityDisposition(cell_id=100, entity_id=1)
        )
        self.game_state.entity.set_actor(actor)

        msg = FightPlacementPossiblePositionsEvent(
            starting_positions=FightStartingPositions(
                challengers_positions=[100, 101, 102],
                defenders_positions=[200, 201, 202],
            )
        )

        self.inject(msg)

        assert self.game_state.fight.fight_placement_possible_positions == [
            100,
            101,
            102,
        ]

    def test_fight_placement_positions_for_defender(self):
        # Setup: create player actor at cell 200 (in defenders)
        self.game_state.player.character_id = 1
        actor = ActorPositionInformation(
            actor_id=1, disposition=EntityDisposition(cell_id=200, entity_id=1)
        )
        self.game_state.entity.set_actor(actor)

        msg = FightPlacementPossiblePositionsEvent(
            starting_positions=FightStartingPositions(
                challengers_positions=[100, 101, 102],
                defenders_positions=[200, 201, 202],
            )
        )

        self.inject(msg)

        assert self.game_state.fight.fight_placement_possible_positions == [
            200,
            201,
            202,
        ]

    def test_character_characteristics_sets_stats(self):
        characteristics = [
            CharacterCharacteristic(
                characteristic_id=CharacteristicEnum.AGILITY,
                value=CharacterCharacteristicValue(total=500),
            ),
            CharacterCharacteristic(
                characteristic_id=CharacteristicEnum.STRENGTH,
                value=CharacterCharacteristicValue(total=300),
            ),
        ]
        msg = CharacterCharacteristicsEvent(
            stats=CharacterCharacteristics(characteristics=characteristics)
        )

        self.inject(msg)

        assert CharacteristicEnum.AGILITY in self.game_state.fight.characteristic_by_id
        assert CharacteristicEnum.STRENGTH in self.game_state.fight.characteristic_by_id

    def test_update_life_points_sets_life(self):
        msg = UpdateLifePointsEvent(life_points=500, max_life_points=1000)

        self.inject(msg)

        assert self.game_state.fight.life_point == 500
        assert self.game_state.fight.max_life_point == 1000

    def test_game_action_fight_cast_increments_count(self):
        spell_id = 42

        self.inject(GameActionFightCastRequest(spell_id=spell_id, cell=100))
        self.inject(GameActionFightCastRequest(spell_id=spell_id, cell=100))

        assert (
            self.game_state.fight.count_casted_by_spell_id_on_current_turn[spell_id]
            == 2
        )

    def test_life_points_gain_updates_life(self):
        self.game_state.fight.life_point = 500
        self.game_state.player.character_id = 123
        msg = GameActionFightEvent(
            life_points_gain=GameActionFightEvent.LifePointsGain(
                target_id=123, delta=100
            )
        )

        self.inject(msg)

        assert self.game_state.fight.life_point == 600

    def test_life_points_lost_updates_life(self):
        self.game_state.fight.life_point = 500
        self.game_state.player.character_id = 123
        msg = GameActionFightEvent(
            life_points_lost=GameActionFightEvent.LifePointsLost(
                target_id=123, loss=150
            )
        )

        self.inject(msg)

        assert self.game_state.fight.life_point == 350

    def test_map_complementary_resets_fight_state(self):
        self.game_state.fight.in_fight = True
        self.game_state.fight.is_our_turn = True
        self.game_state.fight.fight_turn = 5
        self.game_state.fight.is_map_fight_initialized = True

        self.inject(MapComplementaryInformationEvent())

        assert self.game_state.fight.in_fight is False
        assert self.game_state.fight.is_our_turn is False
        assert self.game_state.fight.fight_turn == 0
        assert self.game_state.fight.is_map_fight_initialized is False

    def test_life_percentage_calculation(self):
        self.game_state.fight.life_point = 250
        self.game_state.fight.max_life_point = 1000

        assert self.game_state.fight.life_percentage == 0.25

    def test_multiple_turns_increment_correctly(self):
        self.game_state.fight.fight_turn = 0

        self.inject(FightTurnStartPlayingEvent())
        self.inject(FightTurnFinishRequest())
        self.inject(FightTurnStartPlayingEvent())
        self.inject(FightTurnFinishRequest())
        self.inject(FightTurnStartPlayingEvent())

        assert self.game_state.fight.fight_turn == 3
        assert self.game_state.fight.is_our_turn is True
