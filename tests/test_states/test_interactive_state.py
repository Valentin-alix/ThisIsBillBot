from datas.protos.non_obf.game.common_pb2 import (
    InteractiveElement,
    StatedElement,
)
from datas.protos.non_obf.game.interactive_element_pb2 import (
    InteractiveElementUpdatedEvent,
    InteractiveMapUpdateEvent,
    StatedElementUpdatedEvent,
    StatedMapUpdateEvent,
)

from src.core.bot.bot import Bot
from tests.fixtures.interactives import make_collectable


class TestInteractiveState:
    def test_stated_element_updated_event_replaces_existing_element(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.interactive.set_stated_element(
            StatedElement(
                element_id=10,
                cell_id=100,
                state=1,
                on_current_map=True,
            )
        )

        runtime_bot.event_manager.process_msg(
            StatedElementUpdatedEvent(
                stated_element=StatedElement(
                    element_id=10,
                    cell_id=100,
                    state=2,
                    on_current_map=True,
                )
            )
        )

        stored_element, _ = runtime_bot.game_state.interactive.stated_element_by_id[10]
        assert stored_element.state == 2

    def test_interactive_element_updated_event_adds_element(
        self,
        runtime_bot: Bot,
    ):
        interactive_element = InteractiveElement(
            element_id=99,
            element_type_id=7,
        )

        runtime_bot.event_manager.process_msg(
            InteractiveElementUpdatedEvent(interactive_element=interactive_element)
        )

        assert (
            runtime_bot.game_state.interactive.interactive_element_by_id[99]
            == interactive_element
        )

    def test_interactive_map_update_event_merges_elements(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.interactive.interactive_element_by_id[1] = (
            InteractiveElement(
                element_id=1,
                element_type_id=1,
            )
        )

        runtime_bot.event_manager.process_msg(
            InteractiveMapUpdateEvent(
                interactive_elements=[
                    InteractiveElement(element_id=2, element_type_id=2),
                    InteractiveElement(element_id=3, element_type_id=3),
                ]
            )
        )

        assert set(runtime_bot.game_state.interactive.interactive_element_by_id) == {
            1,
            2,
            3,
        }

    def test_stated_map_update_event_replaces_snapshot(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.interactive.set_stated_elements(
            [
                StatedElement(
                    element_id=10,
                    cell_id=100,
                    on_current_map=True,
                )
            ]
        )

        runtime_bot.event_manager.process_msg(
            StatedMapUpdateEvent(
                stated_elements=[
                    StatedElement(
                        element_id=20,
                        cell_id=200,
                        on_current_map=True,
                    )
                ]
            )
        )

        assert set(runtime_bot.game_state.interactive.stated_element_by_id) == {20}

    def test_get_farmable_collectables_excludes_specified_ids(
        self,
        runtime_bot: Bot,
    ):
        stated_element_10 = StatedElement(
            element_id=10,
            cell_id=100,
            on_current_map=True,
        )
        stated_element_20 = StatedElement(
            element_id=20,
            cell_id=200,
            on_current_map=True,
        )

        runtime_bot.game_state.interactive.stated_element_by_id = {
            10: (
                stated_element_10,
                make_collectable(stated_element_10.element_id),
            ),
            20: (
                stated_element_20,
                make_collectable(stated_element_20.element_id),
            ),
        }

        collectables = runtime_bot.game_state.interactive.get_farmable_collectables(
            excluded_element_ids={10}
        )

        assert [
            collectable.interactive_element.element_id for collectable in collectables
        ] == [20]

    def test_set_stated_element_updates_cell_id_index_on_move(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.interactive.set_stated_element(
            StatedElement(
                element_id=10,
                cell_id=100,
                on_current_map=True,
            )
        )

        runtime_bot.game_state.interactive.set_stated_element(
            StatedElement(
                element_id=10,
                cell_id=200,
                on_current_map=True,
            )
        )

        assert (
            10
            not in runtime_bot.game_state.interactive.stated_element_by_cell_id.get(
                100,
                {},  # pyright: ignore[reportUnknownArgumentType]
            )
        )
        assert 10 in runtime_bot.game_state.interactive.stated_element_by_cell_id[200]

    def test_set_stated_elements_ignores_elements_not_on_current_map_and_replaces_snapshot(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.interactive.set_stated_elements(
            [
                StatedElement(element_id=10, cell_id=100, on_current_map=True),
            ]
        )

        runtime_bot.game_state.interactive.set_stated_elements(
            [
                StatedElement(element_id=20, cell_id=200, on_current_map=False),
                StatedElement(element_id=30, cell_id=300, on_current_map=True),
            ]
        )

        assert set(runtime_bot.game_state.interactive.stated_element_by_id) == {30}
