from DBDofusUnity.datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    CharacterCharacteristic,
    CharacterCharacteristicValue,
    Direction,
    EntityDisposition,
    FightCharacteristics,
    SpawnInformation,
    Team,
)
from DBDofusUnity.datas.protos.non_obf.game.context_pb2 import (
    ContextRemoveElementEvent,
    ContextRemoveElementsEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.fight_pb2 import (
    FightSynchronizeEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.game_action_pb2 import (
    EntitySpawnInformation,
    GameActionFightEvent,
)
from DBDofusUnity.datas.protos.non_obf.game.gamemap_pb2 import (
    GameRolePlayShowActorsEvent,
    MapChangeOrientationEvent,
    MapComplementaryInformationEvent,
    MapMovementEvent,
    MapObstacle,
    MapObstacleUpdateEvent,
)
from DBDofusUnity.dofus_unity_reader.grid.map_point import MapPoint

from src.core.bot.bot import Bot
from src.core.states.entity_state import FightActor
from tests.fixtures.entities import make_actor, make_fighter


class TestEntityState:
    def test_map_complementary_information_event_sets_actors(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=1, cell_id=101),
                make_actor(actor_id=2, cell_id=102),
            ],
        )

        assert set(runtime_bot.game_state.entity.actor_by_id) == {1, 2}
        assert runtime_bot.game_state.entity.actor_by_id[1].disposition.cell_id == 101
        assert runtime_bot.game_state.entity.actor_by_id[2].disposition.cell_id == 102

    def test_map_movement_event_updates_actor_position(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=789, cell_id=100),
            ],
        )

        runtime_bot.event_manager.process_msg(
            MapMovementEvent(
                character_id=789,
                cells=[100, 115, 130],
                direction=1,
            )
        )

        assert runtime_bot.game_state.entity.actor_by_id[789].disposition.cell_id == 130

    def test_context_remove_element_events_remove_actors(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=1, cell_id=100),
                make_actor(actor_id=2, cell_id=101),
                make_actor(actor_id=3, cell_id=102),
            ],
        )

        runtime_bot.event_manager.process_msg(ContextRemoveElementEvent(element_id=1))
        runtime_bot.event_manager.process_msg(ContextRemoveElementsEvent(element_id=[2, 3]))

        assert runtime_bot.game_state.entity.actor_by_id == {}

    def test_game_role_play_show_actors_event_adds_partial_actors(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            GameRolePlayShowActorsEvent(
                actors=[
                    make_actor(actor_id=33, cell_id=120),
                ]
            )
        )

        assert runtime_bot.game_state.entity.actor_by_id[33].disposition.cell_id == 120

    def test_map_obstacle_update_event_updates_obstacles(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            MapObstacleUpdateEvent(
                obstacles=[
                    MapObstacle(
                        cell_id=100,
                        state=MapObstacle.ObstacleState.OBSTACLE_CLOSED,
                    ),
                    MapObstacle(
                        cell_id=101,
                        state=MapObstacle.ObstacleState.OBSTACLE_CLOSED,
                    ),
                ]
            )
        )

        assert set(runtime_bot.game_state.entity.obstacle_on_cell_id) == {100, 101}

    def test_map_change_orientation_event_updates_actor_direction(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(
                    actor_id=789,
                    cell_id=100,
                    direction=Direction.DIRECTION_EAST,
                ),
            ],
        )

        runtime_bot.event_manager.process_msg(
            MapChangeOrientationEvent(
                actor_id=789,
                direction=Direction.DIRECTION_NORTH_EAST,
            )
        )

        assert (
            runtime_bot.game_state.entity.actor_by_id[789].disposition.direction
            == Direction.DIRECTION_NORTH_EAST
        )

    def test_actors_on_mp_index_is_updated_when_setting_actors(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=111, cell_id=256),
            ],
        )

        mp = MapPoint.from_cell_id(256)

        assert 111 in runtime_bot.game_state.entity.actors_on_mp[mp]

    def test_map_complementary_information_event_replaces_previous_actors(
        self,
        runtime_bot: Bot,
    ):
        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=1, cell_id=101),
                make_actor(actor_id=2, cell_id=102),
            ],
        )

        self._set_actors(
            runtime_bot,
            [
                make_actor(actor_id=100, cell_id=50),
            ],
        )

        assert set(runtime_bot.game_state.entity.actor_by_id) == {100}

    def test_fight_synchronize_event_drops_dead_fighters_before_alive_ones(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            FightSynchronizeEvent(fighters=[make_fighter(actor_id=3, cell_id=204, alive=True)])
        )

        runtime_bot.event_manager.process_msg(
            FightSynchronizeEvent(
                fighters=[
                    make_fighter(actor_id=1, cell_id=396, alive=True),
                    make_fighter(actor_id=3, cell_id=204, alive=False),
                    make_fighter(actor_id=2, cell_id=259, alive=True),
                ]
            )
        )

        assert set(runtime_bot.game_state.entity.actor_by_id) == {1, 2}
        enemy_cells = {
            enemy.disposition.cell_id for enemy in runtime_bot.game_state.fight.get_enemies(character_id=0)
        }
        assert 204 not in enemy_cells

    def test_partial_fight_synchronize_keeps_omitted_alive_fighter(
        self,
        runtime_bot: Bot,
    ) -> None:
        runtime_bot.event_manager.process_msg(
            FightSynchronizeEvent(
                fighters=[
                    make_fighter(actor_id=-1, cell_id=396, alive=True),
                    make_fighter(actor_id=-2, cell_id=204, alive=True),
                ]
            )
        )

        runtime_bot.event_manager.process_msg(
            FightSynchronizeEvent(fighters=[make_fighter(actor_id=-1, cell_id=396, alive=True)])
        )

        assert set(runtime_bot.game_state.entity.actor_by_id) == {-1, -2}

    def test_fight_synchronize_recreates_revived_fight_actor(self, runtime_bot: Bot) -> None:
        revived_fighter = make_fighter(actor_id=-2, cell_id=204, alive=True)
        revived_fighter.actor_information.fighter.stats.characteristics.append(
            CharacterCharacteristic(
                characteristic_id=0,
                value=CharacterCharacteristicValue(total=300),
            )
        )
        runtime_bot.game_state.entity.set_actor(revived_fighter)
        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                death=GameActionFightEvent.Death(target_id=-2),
            )
        )

        runtime_bot.event_manager.process_msg(FightSynchronizeEvent(fighters=[revived_fighter]))

        assert runtime_bot.game_state.entity.actor_fight_by_id[-2].life_point == 300

    def test_context_summons_create_fight_actors_before_life_loss(
        self,
        runtime_bot: Bot,
    ) -> None:
        runtime_bot.game_state.entity.actor_by_id[-3] = make_fighter(
            actor_id=-3,
            cell_id=291,
            team=Team.TEAM_DEFENDER,
        )
        runtime_bot.game_state.entity.actor_fight_by_id[-3] = FightActor(
            life_point=120,
            is_summoned=False,
        )

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                action_id=181,
                source_id=-3,
                summons=GameActionFightEvent.Summons(
                    summons_by_context_information=GameActionFightEvent.Summons.SummonsByContextInformation(
                        summons=[
                            GameActionFightEvent.Summons.SummonsByContextInformation.SummonContextInformation(
                                spawn_information=EntitySpawnInformation(
                                    monster=EntitySpawnInformation.Monster(
                                        monster_gid=5232,
                                        grade=1,
                                    )
                                ),
                                wave=0,
                                characteristics=FightCharacteristics(
                                    summoned=True,
                                    summoner=-3,
                                    characteristics=[
                                        CharacterCharacteristic(
                                            characteristic_id=0,
                                            value=CharacterCharacteristicValue(total=75),
                                        )
                                    ],
                                ),
                                summons=[
                                    SpawnInformation(
                                        alive=True,
                                        team=Team.TEAM_DEFENDER,
                                        position=ActorPositionInformation(
                                            actor_id=-11,
                                            disposition=EntityDisposition(
                                                cell_id=329,
                                                direction=Direction.DIRECTION_EAST,
                                                entity_id=-11,
                                            ),
                                        ),
                                    )
                                ],
                            )
                        ]
                    )
                ),
            )
        )

        runtime_bot.event_manager.process_msg(
            GameActionFightEvent(
                action_id=96,
                source_id=71808188767,
                life_points_lost=GameActionFightEvent.LifePointsLost(
                    target_id=-11,
                    loss=70,
                    permanent_damages=3,
                    element_id=7,
                ),
            )
        )

        assert runtime_bot.game_state.entity.actor_by_id[-11].disposition.cell_id == 329
        actor_fight = runtime_bot.game_state.entity.actor_fight_by_id[-11]
        assert actor_fight.is_summoned is True
        assert actor_fight.life_point == 5

    def test_get_enemies_only_returns_other_teams(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            FightSynchronizeEvent(
                fighters=[
                    make_fighter(actor_id=100, cell_id=272, team=Team.TEAM_CHALLENGER),
                    make_fighter(actor_id=200, cell_id=280, team=Team.TEAM_CHALLENGER),
                    make_fighter(actor_id=300, cell_id=259, team=Team.TEAM_DEFENDER),
                    make_fighter(actor_id=400, cell_id=396, team=Team.TEAM_DEFENDER),
                ]
            )
        )

        enemies = runtime_bot.game_state.fight.get_enemies(character_id=100)

        assert {enemy.actor_id for enemy in enemies} == {300, 400}

    def _set_actors(
        self,
        runtime_bot: Bot,
        actors: list[ActorPositionInformation],
    ) -> None:
        runtime_bot.event_manager.process_msg(MapComplementaryInformationEvent(actors=actors))
