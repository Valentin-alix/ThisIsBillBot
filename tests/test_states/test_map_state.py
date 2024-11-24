from ProtoMapperAssembly.data.non_obf.protos.game.common_pb2 import (
    ActorPositionInformation,
    EntityDisposition,
)
from ProtoMapperAssembly.data.non_obf.protos.game.gamemap_pb2 import (
    FightMapInformationEvent,
    MapCurrentEvent,
)
from tests.test_states.state_test_base import StateTestBase


class TestMapState(StateTestBase):
    def test_initial_state(self):
        assert self.game_state.map.map_id == 0
        assert self.game_state.map.is_in_map_transition is False
        assert self.game_state.map.is_in_haven_bag is False

    def test_clear_state_resets_values(self):
        self.game_state.map.map_id = 12345
        self.game_state.map.is_in_map_transition = True
        self.game_state.map.is_in_haven_bag = True

        self.game_state.map.clear_state()

        assert self.game_state.map.map_id == 0
        assert self.game_state.map.is_in_map_transition is False
        assert self.game_state.map.is_in_haven_bag is False

    def test_map_current_event_sets_map_id(self):
        msg = MapCurrentEvent(map_id=12345)

        self.inject(msg)

        assert self.game_state.map.map_id == 12345

    def test_map_current_event_sets_transition_state(self):
        self.game_state.map.is_in_map_transition = False

        msg = MapCurrentEvent(map_id=12345)

        self.inject(msg)

        assert self.game_state.map.is_in_map_transition is True

    def test_map_current_event_clears_actors(self):
        actor = ActorPositionInformation(
            actor_id=1, disposition=EntityDisposition(cell_id=100, entity_id=1)
        )
        self.game_state.entity.set_actor(actor)

        msg = MapCurrentEvent(map_id=12345)

        self.inject(msg)

        assert len(self.game_state.entity.actor_by_id) == 0

    def test_map_current_event_clears_stated_elements(self):
        msg = MapCurrentEvent(map_id=12345)

        self.inject(msg)

        assert len(self.game_state.interactive.stated_element_by_id) == 0

    def test_fight_map_information_ends_transition(self):
        self.game_state.map.is_in_map_transition = True

        self.inject(FightMapInformationEvent())

        assert self.game_state.map.is_in_map_transition is False

    def test_fight_map_information_clears_haven_bag(self):
        self.game_state.map.is_in_haven_bag = True

        self.inject(FightMapInformationEvent())

        assert self.game_state.map.is_in_haven_bag is False

    def test_multiple_map_current_events(self):
        for map_id in [10000, 20000, 30000]:
            self.inject(MapCurrentEvent(map_id=map_id))
            assert self.game_state.map.map_id == map_id
            assert self.game_state.map.is_in_map_transition is True
