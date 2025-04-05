from datas.protos.non_obf.game.character_pb2 import (
    CharacterCharacteristicsEvent,
)
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    CharacterCharacteristicDetailed,
    CharacterCharacteristics,
    CharacterCharacteristicValue,
    EntityDisposition,
    FightStartingPositions,
)
from datas.protos.non_obf.game.fight_preparation_pb2 import (
    FightPlacementPossiblePositionsEvent,
)
from datas.protos.non_obf.game.game_action_pb2 import (
    GameActionFightCastRequest,
    GameActionFightEvent,
)
from datas.protos.non_obf.game.spell_pb2 import SpellItem, SpellsEvent
from dofus_unity_reader.game_constants.characteristic import CharacteristicEnum
from pytest import MonkeyPatch

from src import const
from src.core.bot.bot import Bot
from src.core.states.entity_state import FightActor


class TestFightState:
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
        monkeypatch: MonkeyPatch,
    ):
        monkeypatch.setattr(const, "DEBUG", True)
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

    def test_character_characteristics_event_syncs_life_points(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            CharacterCharacteristicsEvent(
                stats=CharacterCharacteristics(
                    characteristics=[
                        self._detailed_characteristic(
                            CharacteristicEnum.LIFE_POINTS, base=245
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.VITALITY,
                            objects_and_mount_bonus=55,
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.CUR_LIFE, base=0
                        ),
                    ]
                )
            )
        )

        assert runtime_bot.game_state.fight.life_point == 300
        assert runtime_bot.game_state.fight.max_life_point == 300

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

    def test_life_points_lost_death_and_cur_life_sync_update_player_life(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.player.character_id = 8921612638
        runtime_bot.event_manager.process_msg(
            CharacterCharacteristicsEvent(
                stats=CharacterCharacteristics(
                    characteristics=[
                        self._detailed_characteristic(
                            CharacteristicEnum.LIFE_POINTS, base=245
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.VITALITY,
                            objects_and_mount_bonus=55,
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.CUR_LIFE, base=0
                        ),
                    ]
                )
            )
        )

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                life_points_lost=GameActionFightEvent.LifePointsLost(
                    target_id=8921612638,
                    loss=7,
                    permanent_damages=1,
                    element_id=0,
                )
            )
        )

        assert runtime_bot.game_state.fight.life_point == 293

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                death=GameActionFightEvent.Death(
                    target_id=8921612638,
                    source_id=0,
                )
            )
        )

        assert runtime_bot.game_state.fight.life_point == 0

        runtime_bot.event_manager.process_msg(
            CharacterCharacteristicsEvent(
                stats=CharacterCharacteristics(
                    characteristics=[
                        self._detailed_characteristic(
                            CharacteristicEnum.LIFE_POINTS, base=245
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.VITALITY,
                            objects_and_mount_bonus=55,
                        ),
                        self._detailed_characteristic(
                            CharacteristicEnum.CUR_LIFE, base=-150
                        ),
                    ]
                )
            )
        )

        assert runtime_bot.game_state.fight.life_point == 150
        assert runtime_bot.game_state.fight.max_life_point == 300

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

    def _detailed_characteristic(
        self,
        characteristic_id: CharacteristicEnum,
        *,
        base: int = 0,
        objects_and_mount_bonus: int = 0,
    ) -> CharacterCharacteristic:
        return CharacterCharacteristic(
            characteristic_id=characteristic_id,
            detailed=CharacterCharacteristicDetailed(
                base=base,
                objects_and_mount_bonus=objects_and_mount_bonus,
            ),
        )
