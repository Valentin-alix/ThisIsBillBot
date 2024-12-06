from datas.protos.non_obf.game.common_pb2 import (
    InteractiveElement,
    StatedElement,
)
from datas.protos.non_obf.game.interactive_element_pb2 import (
    StatedElementUpdatedEvent,
)
from src.core.bot.bot_factory import BotFactory
from src.core.engine.interactives.collectable import Collectable
from src.core.signals.shared_farm_signals import SharedSignals
from tests.test_states.state_test_base import StateTestBase, TEST_ACCOUNT


def get_fake_collectable(element_id: int):
    return Collectable(
        map_id=1,
        interactive_element=InteractiveElement(
            element_id=element_id, element_type_id=1
        ),
        skill=InteractiveElement.InteractiveElementSkill(
            skill_id=1, skill_instance_uid=1
        ),
        resource_item_id=1,
    )


class TestInteractiveState(StateTestBase):
    def test_initial_state(self):
        assert len(self.game_state.interactive.interactive_element_by_id) == 0
        assert len(self.game_state.interactive.stated_element_by_id) == 0

    def test_collection_fields_are_not_shared_between_instances(self):
        other_bot = BotFactory.create_bot(
            SharedSignals(), account=TEST_ACCOUNT, is_fake=True
        )

        assert (
            self.game_state.interactive.interactive_element_by_id
            is not other_bot.game_state.interactive.interactive_element_by_id
        )
        assert (
            self.game_state.interactive.stated_element_by_id
            is not other_bot.game_state.interactive.stated_element_by_id
        )
        assert (
            self.game_state.interactive.stated_element_by_cell_id
            is not other_bot.game_state.interactive.stated_element_by_cell_id
        )

    def test_clear_state_resets_values(self):
        self.game_state.interactive.interactive_element_by_id[1] = InteractiveElement(
            element_id=1
        )

        self.game_state.interactive.clear_state()

        assert len(self.game_state.interactive.interactive_element_by_id) == 0
        assert len(self.game_state.interactive.stated_element_by_id) == 0

    def test_stated_element_updated_adds_new_element(self):
        stated_element = StatedElement(element_id=10, cell_id=100, on_current_map=True)
        msg = StatedElementUpdatedEvent(stated_element=stated_element)

        self.inject(msg)

        assert 10 in self.game_state.interactive.stated_element_by_id

    def test_stated_element_updated_replaces_existing(self):
        initial_element = StatedElement(
            element_id=10, cell_id=100, state=1, on_current_map=True
        )
        self.game_state.interactive.set_stated_element(initial_element)

        updated_element = StatedElement(
            element_id=10, cell_id=100, state=2, on_current_map=True
        )
        msg = StatedElementUpdatedEvent(stated_element=updated_element)

        self.inject(msg)

        assert 10 in self.game_state.interactive.stated_element_by_id
        stored_element, _ = self.game_state.interactive.stated_element_by_id[10]
        assert stored_element.state == 2

    def test_stated_element_by_cell_id_indexing(self):
        stated_elements = [
            StatedElement(element_id=10, cell_id=100, on_current_map=True),
            StatedElement(element_id=20, cell_id=100, on_current_map=True),
            StatedElement(element_id=30, cell_id=200, on_current_map=True),
        ]
        self.game_state.interactive.set_stated_elements(stated_elements)

        assert 100 in self.game_state.interactive.stated_element_by_cell_id
        assert 200 in self.game_state.interactive.stated_element_by_cell_id
        assert len(self.game_state.interactive.stated_element_by_cell_id[100]) == 2
        assert len(self.game_state.interactive.stated_element_by_cell_id[200]) == 1

    def test_clear_stated_elements(self):
        stated_elements = [
            StatedElement(element_id=10, cell_id=100, on_current_map=True),
            StatedElement(element_id=20, cell_id=200, on_current_map=True),
        ]
        self.game_state.interactive.set_stated_elements(stated_elements)

        self.game_state.interactive.clear_stated_elements()

        assert len(self.game_state.interactive.stated_element_by_id) == 0
        assert len(self.game_state.interactive.stated_element_by_cell_id) == 0

    def test_get_farmable_collectables_empty_when_no_collectables(self):
        stated_elements = [
            StatedElement(element_id=10, cell_id=100, on_current_map=True),
        ]
        self.game_state.interactive.set_stated_elements(stated_elements)

        collectables = self.game_state.interactive.get_farmable_collectables()

        assert collectables == []

    def test_get_farmable_collectables_excludes_specified_ids(self):
        stated_element_10 = StatedElement(
            element_id=10, cell_id=100, on_current_map=True
        )
        stated_element_20 = StatedElement(
            element_id=20, cell_id=200, on_current_map=True
        )
        stated_elements = [stated_element_10, stated_element_20]
        self.game_state.interactive.set_stated_elements(stated_elements)
        self.game_state.interactive.stated_element_by_id[
            stated_element_10.element_id
        ] = (stated_element_10, get_fake_collectable(stated_element_10.element_id))
        self.game_state.interactive.stated_element_by_id[
            stated_element_20.element_id
        ] = (stated_element_20, get_fake_collectable(stated_element_20.element_id))

        collectables = self.game_state.interactive.get_farmable_collectables(
            excluded_element_ids={stated_element_10.element_id}
        )

        assert len(collectables) == 1
        assert (
            collectables[0].interactive_element.element_id
            == stated_element_20.element_id
        )

    def test_set_stated_element_updates_cell_id_index_on_move(self):
        initial_element = StatedElement(element_id=10, cell_id=100, on_current_map=True)
        self.game_state.interactive.set_stated_element(initial_element)

        assert 100 in self.game_state.interactive.stated_element_by_cell_id
        assert 10 in self.game_state.interactive.stated_element_by_cell_id[100]

        moved_element = StatedElement(element_id=10, cell_id=200, on_current_map=True)
        self.game_state.interactive.set_stated_element(moved_element)

        assert 10 not in self.game_state.interactive.stated_element_by_cell_id.get(
            100, {}
        )
        assert 200 in self.game_state.interactive.stated_element_by_cell_id
        assert 10 in self.game_state.interactive.stated_element_by_cell_id[200]

    def test_stated_element_by_cell_id_auto_creates_dict(self):
        cell_dict = self.game_state.interactive.stated_element_by_cell_id[999]

        assert cell_dict.cell_id == 999
        assert isinstance(cell_dict, dict)

    def test_stated_element_not_on_current_map_ignored(self):
        stated_elements = [
            StatedElement(element_id=10, cell_id=100, on_current_map=True),
            StatedElement(element_id=20, cell_id=200, on_current_map=False),
        ]

        self.game_state.interactive.set_stated_elements(stated_elements)

        assert len(self.game_state.interactive.stated_element_by_id) == 1
        assert 10 in self.game_state.interactive.stated_element_by_id
        assert 20 not in self.game_state.interactive.stated_element_by_id

    def test_set_interactive_elements_directly(self):
        self.game_state.interactive.interactive_element_by_id = {
            1: InteractiveElement(element_id=1),
            2: InteractiveElement(element_id=2),
            3: InteractiveElement(element_id=3),
        }

        assert len(self.game_state.interactive.interactive_element_by_id) == 3
        assert 1 in self.game_state.interactive.interactive_element_by_id
        assert 2 in self.game_state.interactive.interactive_element_by_id
        assert 3 in self.game_state.interactive.interactive_element_by_id

    def test_new_stated_elements_clears_old_ones(self):
        initial_elements = [
            StatedElement(element_id=10, cell_id=100, on_current_map=True),
        ]
        self.game_state.interactive.set_stated_elements(initial_elements)

        new_elements = [
            StatedElement(element_id=50, cell_id=500, on_current_map=True),
        ]
        self.game_state.interactive.set_stated_elements(new_elements)

        assert 10 not in self.game_state.interactive.stated_element_by_id
        assert 50 in self.game_state.interactive.stated_element_by_id
