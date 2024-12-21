from collections.abc import Mapping

from dofus_unity_reader.grid.map_point import MapPoint
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
    Direction,
    EntityDisposition,
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
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from src.core.states.entity_state import ActorByMpDict
from src.utils.dataclass_utils import dataclass_to_dict
from src.utils.protobuf_utils import apply_dict_to_dataclass
from tests.test_states.state_test_base import StateTestBase, TEST_ACCOUNT


class TestEntityState(StateTestBase):
    def test_collection_fields_are_not_shared_between_instances(self):
        other_bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )

        assert (
            self.game_state.entity.actor_by_id
            is not other_bot.game_state.entity.actor_by_id
        )
        assert (
            self.game_state.entity.actor_fight_by_id
            is not other_bot.game_state.entity.actor_fight_by_id
        )
        assert (
            self.game_state.entity.obstacle_on_cell_id
            is not other_bot.game_state.entity.obstacle_on_cell_id
        )
        assert (
            self.game_state.entity.actors_on_mp
            is not other_bot.game_state.entity.actors_on_mp
        )

    def test_set_actors_from_map_complementary_info(self):
        actor = ActorPositionInformation(
            actor_id=123,
            disposition=EntityDisposition(cell_id=300, entity_id=123),
        )
        msg = MapComplementaryInformationEvent(actors=[actor])

        self.inject(msg)

        assert 123 in self.game_state.entity.actor_by_id
        assert self.game_state.entity.actor_by_id[123].disposition.cell_id == 300

    def test_set_multiple_actors(self):
        actors = [
            ActorPositionInformation(
                actor_id=i, disposition=EntityDisposition(cell_id=100 + i, entity_id=i)
            )
            for i in range(5)
        ]
        self.inject(MapComplementaryInformationEvent(actors=actors))

        assert len(self.game_state.entity.actor_by_id) == 5
        for i in range(5):
            assert i in self.game_state.entity.actor_by_id

    def test_update_actor_position_on_movement(self):
        actor = ActorPositionInformation(
            actor_id=789, disposition=EntityDisposition(cell_id=100, entity_id=789)
        )
        self.inject(MapComplementaryInformationEvent(actors=[actor]))

        self.inject(
            MapMovementEvent(character_id=789, cells=[100, 115, 130], direction=1)
        )

        assert self.game_state.entity.actor_by_id[789].disposition.cell_id == 130

    def test_context_remove_element_event_removes_actor(self):
        actor = ActorPositionInformation(
            actor_id=789, disposition=EntityDisposition(cell_id=100, entity_id=789)
        )
        self.inject(MapComplementaryInformationEvent(actors=[actor]))

        self.inject(ContextRemoveElementEvent(element_id=789))

        assert 789 not in self.game_state.entity.actor_by_id

    def test_context_remove_elements_event_removes_multiple_actors(self):
        actors = [
            ActorPositionInformation(
                actor_id=1, disposition=EntityDisposition(cell_id=100, entity_id=1)
            ),
            ActorPositionInformation(
                actor_id=2, disposition=EntityDisposition(cell_id=101, entity_id=2)
            ),
        ]
        self.inject(MapComplementaryInformationEvent(actors=actors))

        self.inject(ContextRemoveElementsEvent(element_id=[1, 2]))

        assert len(self.game_state.entity.actor_by_id) == 0

    def test_game_role_play_show_actors_event_adds_partial_actors(self):
        self.inject(
            GameRolePlayShowActorsEvent(
                actors=[
                    ActorPositionInformation(
                        actor_id=33,
                        disposition=EntityDisposition(cell_id=120, entity_id=33),
                    )
                ]
            )
        )

        assert self.game_state.entity.actor_by_id[33].disposition.cell_id == 120

    def test_map_obstacle_update_event_updates_obstacles(self):
        self.inject(
            MapObstacleUpdateEvent(
                obstacles=[
                    MapObstacle(
                        cell_id=100, state=MapObstacle.ObstacleState.OBSTACLE_CLOSED
                    ),
                    MapObstacle(
                        cell_id=101, state=MapObstacle.ObstacleState.OBSTACLE_CLOSED
                    ),
                ]
            )
        )

        assert set(self.game_state.entity.obstacle_on_cell_id) == {100, 101}

    def test_map_change_orientation_event_updates_actor_direction(self):
        actor = ActorPositionInformation(
            actor_id=789,
            disposition=EntityDisposition(
                cell_id=100,
                entity_id=789,
                direction=Direction.DIRECTION_EAST,
            ),
        )
        self.inject(MapComplementaryInformationEvent(actors=[actor]))

        self.inject(
            MapChangeOrientationEvent(
                actor_id=789, direction=Direction.DIRECTION_NORTH_EAST
            )
        )

        assert (
            self.game_state.entity.actor_by_id[789].disposition.direction
            == Direction.DIRECTION_NORTH_EAST
        )

    def test_actors_on_mp_updated(self):
        actor = ActorPositionInformation(
            actor_id=111, disposition=EntityDisposition(cell_id=256, entity_id=111)
        )
        self.inject(MapComplementaryInformationEvent(actors=[actor]))

        mp = MapPoint.from_cell_id(256)
        assert mp in self.game_state.entity.actors_on_mp
        assert 111 in self.game_state.entity.actors_on_mp[mp]

    def test_clear_actors_on_new_map(self):
        actors = [
            ActorPositionInformation(
                actor_id=i, disposition=EntityDisposition(cell_id=100 + i, entity_id=i)
            )
            for i in range(3)
        ]
        self.inject(MapComplementaryInformationEvent(actors=actors))
        assert len(self.game_state.entity.actor_by_id) == 3

        new_actors = [
            ActorPositionInformation(
                actor_id=100, disposition=EntityDisposition(cell_id=50, entity_id=100)
            )
        ]
        self.inject(MapComplementaryInformationEvent(actors=new_actors))

        assert len(self.game_state.entity.actor_by_id) == 1
        assert 100 in self.game_state.entity.actor_by_id

    def test_actors_on_mp_type_preserved_after_serialization(self):
        actor = ActorPositionInformation(
            actor_id=123, disposition=EntityDisposition(cell_id=256, entity_id=123)
        )
        self.inject(MapComplementaryInformationEvent(actors=[actor]))

        assert isinstance(self.game_state.entity.actors_on_mp, ActorByMpDict)

        state_dict: Mapping[str, object] = dataclass_to_dict(self.game_state.entity)

        apply_dict_to_dataclass(self.game_state.entity, state_dict)

        assert isinstance(self.game_state.entity.actors_on_mp, ActorByMpDict), (
            f"Expected ActorByMpDict but got {type(self.game_state.entity.actors_on_mp)}"
        )
