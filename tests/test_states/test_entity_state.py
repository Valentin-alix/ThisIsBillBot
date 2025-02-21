from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    Direction,
)
from datas.protos.non_obf.game.context_pb2 import (
    ContextRemoveElementEvent,
    ContextRemoveElementsEvent,
)
from datas.protos.non_obf.game.gamemap_pb2 import (
    GameRolePlayShowActorsEvent,
    MapChangeOrientationEvent,
    MapComplementaryInformationEvent,
    MapMovementEvent,
    MapObstacle,
    MapObstacleUpdateEvent,
)
from dofus_unity_reader.grid.map_point import MapPoint

from src.core.bot.bot import Bot
from tests.fixtures.entities import make_actor


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
        runtime_bot.event_manager.process_msg(
            ContextRemoveElementsEvent(element_id=[2, 3])
        )

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

    def _set_actors(
        self,
        runtime_bot: Bot,
        actors: list[ActorPositionInformation],
    ) -> None:
        runtime_bot.event_manager.process_msg(
            MapComplementaryInformationEvent(actors=actors)
        )
