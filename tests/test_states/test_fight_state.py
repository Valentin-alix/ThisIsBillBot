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
    FightEndEvent,
    FightTurnEndEvent,
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
)
from datas.protos.non_obf.game.spell_pb2 import SpellItem, SpellsEvent
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum

from src.core.bot.bot import Bot
from src.core.states.entity_state import FightActor


class TestFightState:
    def test_fight_map_information_then_turn_start_clears_start_fight_state(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn[123] = 5
        runtime_bot.game_state.fight.modifier_by_type_and_spell_id[
            (1, SpellModifierType.RANGE)
        ] = SpellModifier()

        runtime_bot.event_manager.process_msg(FightMapInformationEvent())
        runtime_bot.event_manager.process_msg(FightTurnStartPlayingEvent())

        assert (
            runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn == {}
        )
        assert runtime_bot.game_state.fight.modifier_by_type_and_spell_id == {}

    def test_spells_event_sets_spells(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            SpellsEvent(
                human_spells=[
                    SpellItem(spell_id=100, spell_level=1, available=True),
                    SpellItem(spell_id=200, spell_level=2, available=True),
                ]
            )
        )

        assert [spell.spell_id for spell in runtime_bot.game_state.fight.spells] == [
            100,
            200,
        ]

    def test_fight_turn_start_playing_sets_our_turn_and_increments(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.fight.is_our_turn = False
        runtime_bot.game_state.fight.fight_turn = 0

        runtime_bot.event_manager.process_msg(FightTurnStartPlayingEvent())

        assert runtime_bot.game_state.fight.is_our_turn is True
        assert runtime_bot.game_state.fight.fight_turn == 1

    def test_fight_placement_positions_for_challenger(
        self,
        runtime_bot: Bot,
    ):
        self._set_player_actor_cell(runtime_bot, cell_id=100)

        runtime_bot.event_manager.process_msg(
            FightPlacementPossiblePositionsEvent(
                starting_positions=FightStartingPositions(
                    challengers_positions=[100, 101, 102],
                    defenders_positions=[200, 201, 202],
                )
            )
        )

        assert runtime_bot.game_state.fight.fight_placement_possible_positions == [
            100,
            101,
            102,
        ]

    def test_fight_placement_positions_for_defender(
        self,
        runtime_bot: Bot,
    ):
        self._set_player_actor_cell(runtime_bot, cell_id=200)

        runtime_bot.event_manager.process_msg(
            FightPlacementPossiblePositionsEvent(
                starting_positions=FightStartingPositions(
                    challengers_positions=[100, 101, 102],
                    defenders_positions=[200, 201, 202],
                )
            )
        )

        assert runtime_bot.game_state.fight.fight_placement_possible_positions == [
            200,
            201,
            202,
        ]

    def test_character_characteristics_event_sets_stats_and_emits_points(
        self,
        runtime_bot: Bot,
    ):
        received_action_points: list[int] = []
        received_movement_points: list[int] = []

        runtime_bot.game_info_signals.action_points.connect(
            received_action_points.append
        )
        runtime_bot.game_info_signals.movement_points.connect(
            received_movement_points.append
        )

        runtime_bot.event_manager.process_msg(
            CharacterCharacteristicsEvent(
                stats=CharacterCharacteristics(
                    characteristics=[
                        CharacterCharacteristic(
                            characteristic_id=CharacteristicEnum.ACTION_POINTS,
                            value=CharacterCharacteristicValue(total=12),
                        ),
                        CharacterCharacteristic(
                            characteristic_id=CharacteristicEnum.MOVEMENT_POINTS,
                            value=CharacterCharacteristicValue(total=6),
                        ),
                    ]
                )
            )
        )

        assert (
            CharacteristicEnum.ACTION_POINTS
            in runtime_bot.game_state.fight.characteristic_by_id
        )
        assert (
            CharacteristicEnum.MOVEMENT_POINTS
            in runtime_bot.game_state.fight.characteristic_by_id
        )
        assert received_action_points == [12]
        assert received_movement_points == [6]

    def test_update_life_points_event_sets_life(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            UpdateLifePointsEvent(
                life_points=500,
                max_life_points=1000,
            )
        )

        assert runtime_bot.game_state.fight.life_point == 500
        assert runtime_bot.game_state.fight.max_life_point == 1000

    def test_game_action_fight_cast_request_increments_count_by_spell_id(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            GameActionFightCastRequest(
                spell_id=42,
                cell=100,
            )
        )
        runtime_bot.event_manager.process_msg(
            GameActionFightCastRequest(
                spell_id=42,
                cell=100,
            )
        )

        assert (
            runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn[42]
            == 2
        )

    def test_life_points_gain_and_loss_update_player_life(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.fight.life_point = 500
        runtime_bot.game_state.player.character_id = 123
        runtime_bot.game_state.entity.actor_fight_by_id[
            runtime_bot.game_state.player.character_id
        ] = FightActor(
            life_point=runtime_bot.game_state.fight.life_point, is_summoned=False
        )

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                life_points_gain=GameActionFightEvent.LifePointsGain(
                    target_id=123,
                    delta=100,
                )
            )
        )

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                life_points_lost=GameActionFightEvent.LifePointsLost(
                    target_id=123,
                    loss=150,
                )
            )
        )

        assert runtime_bot.game_state.fight.life_point == 450

    def test_fight_turn_end_event_clears_our_turn_for_player(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.player.character_id = 123
        runtime_bot.game_state.fight.is_our_turn = True
        runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn[42] = 1

        runtime_bot.event_manager.process_msg(FightTurnEndEvent(character_id=123))

        assert runtime_bot.game_state.fight.is_our_turn is False
        assert (
            runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn == {}
        )

    def test_fight_end_event_resets_fight_flags(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.fight.in_fight = True
        runtime_bot.game_state.fight.is_our_turn = True
        runtime_bot.game_state.fight.fight_turn = 3
        runtime_bot.game_state.fight.is_map_fight_initialized = True
        runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn[42] = 1

        runtime_bot.event_manager.process_msg(FightEndEvent())

        assert runtime_bot.game_state.fight.in_fight is False
        assert runtime_bot.game_state.fight.is_our_turn is False
        assert runtime_bot.game_state.fight.fight_turn == 0
        assert runtime_bot.game_state.fight.is_map_fight_initialized is False
        assert (
            runtime_bot.game_state.fight.count_casted_by_spell_id_on_current_turn == {}
        )

    def _set_player_actor_cell(
        self,
        runtime_bot: Bot,
        *,
        cell_id: int,
    ) -> None:
        runtime_bot.game_state.player.character_id = 1
        runtime_bot.game_state.entity.set_actor(
            ActorPositionInformation(
                actor_id=1,
                disposition=EntityDisposition(
                    cell_id=cell_id,
                    entity_id=1,
                ),
            )
        )
