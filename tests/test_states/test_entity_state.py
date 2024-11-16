from D3Database.grid.map_point import MapPoint
from D3Mapping.d3_mapping.resources.protos.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from D3Mapping.d3_mapping.resources.protos.game.gamemap_pb2 import (
    MapComplementaryInformationEvent,
    MapMovementEvent,
)
from src.core.states.entity_state import ActorByMpDict
from src.utils.dataclass_utils import apply_dict_to_dataclass, dataclass_to_dict
from tests.test_states.state_test_base import StateTestBase


class TestEntityState(StateTestBase):
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

        state_dict = dataclass_to_dict(self.game_state.entity)

        apply_dict_to_dataclass(self.game_state.entity, state_dict)

        assert isinstance(
            self.game_state.entity.actors_on_mp, ActorByMpDict
        ), f"Expected ActorByMpDict but got {type(self.game_state.entity.actors_on_mp)}"
