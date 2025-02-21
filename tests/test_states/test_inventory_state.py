import pytest
from datas.protos.non_obf.game.common_pb2 import (
    ObjectUidWithQuantity,
)
from datas.protos.non_obf.game.inventory_pb2 import (
    InventoryContentEvent,
    InventoryWeightEvent,
    KamasUpdateEvent,
    ObjectAddedEvent,
    ObjectDeletedEvent,
    ObjectModifiedEvent,
    ObjectQuantityEvent,
    ObjectsAddedEvent,
    ObjectsDeletedEvent,
    ObjectsQuantityEvent,
)

from src.core.bot.bot import Bot
from tests.fixtures.inventory import make_inventory_item


class TestInventoryState:
    def test_inventory_content_event_sets_objects_and_kamas(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            InventoryContentEvent(
                objects=[
                    make_inventory_item(gid=100, quantity=10, uid=1),
                    make_inventory_item(gid=200, quantity=5, uid=2),
                ],
                kamas=50000,
            )
        )

        assert runtime_bot.game_state.inventory.objects_by_uid.keys() == {1, 2}
        assert runtime_bot.game_state.inventory.kamas == 50000

    def test_object_added_events_add_objects(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            ObjectAddedEvent(
                object=make_inventory_item(
                    gid=100,
                    uid=1,
                    quantity=10,
                )
            )
        )

        runtime_bot.event_manager.process_msg(
            ObjectsAddedEvent(
                objects=[
                    make_inventory_item(
                        uid=2,
                        gid=200,
                        quantity=5,
                    )
                ]
            )
        )

        assert runtime_bot.game_state.inventory.objects_by_uid.keys() == {1, 2}

    def test_object_deleted_events_remove_objects(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.inventory.add_objects(
            [
                make_inventory_item(uid=1, gid=100, quantity=10),
                make_inventory_item(uid=2, gid=200, quantity=5),
            ]
        )

        runtime_bot.event_manager.process_msg(ObjectDeletedEvent(object_uid=1))

        runtime_bot.event_manager.process_msg(ObjectsDeletedEvent(objects_uid=[2]))

        assert runtime_bot.game_state.inventory.objects_by_uid == {}

    def test_object_quantity_events_update_quantities(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.inventory.add_objects(
            [
                make_inventory_item(uid=1, gid=100, quantity=10),
                make_inventory_item(uid=2, gid=200, quantity=5),
            ]
        )

        runtime_bot.event_manager.process_msg(
            ObjectQuantityEvent(
                object=ObjectUidWithQuantity(
                    object_uid=1,
                    quantity=25,
                )
            )
        )

        runtime_bot.event_manager.process_msg(
            ObjectsQuantityEvent(
                object=[
                    ObjectUidWithQuantity(
                        object_uid=2,
                        quantity=8,
                    )
                ]
            )
        )

        assert runtime_bot.game_state.inventory.objects_by_uid[1].item.quantity == 25
        assert runtime_bot.game_state.inventory.objects_by_uid[2].item.quantity == 8

    def test_object_modified_event_replaces_object(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.inventory.add_object(
            make_inventory_item(
                uid=1,
                gid=100,
                quantity=10,
            )
        )

        runtime_bot.event_manager.process_msg(
            ObjectModifiedEvent(
                object=make_inventory_item(
                    uid=1,
                    gid=100,
                    quantity=99,
                )
            )
        )

        assert runtime_bot.game_state.inventory.objects_by_uid[1].item.quantity == 99

    def test_inventory_weight_event_updates_weight(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.event_manager.process_msg(
            InventoryWeightEvent(
                inventory_weight=500,
                weight_max=2000,
            )
        )

        assert runtime_bot.game_state.inventory.inventory_weight == 500
        assert runtime_bot.game_state.inventory.weight_max == 2000

    def test_pod_percentage_calculation(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.inventory.inventory_weight = 500
        runtime_bot.game_state.inventory.weight_max = 1000

        assert runtime_bot.game_state.inventory.pod_percentage == 0.5

    @pytest.mark.parametrize(
        ("weight", "expected"),
        [
            (899, False),
            (900, True),
        ],
    )
    def test_is_full_pods(
        self,
        runtime_bot: Bot,
        weight: int,
        expected: bool,
    ):
        runtime_bot.game_state.inventory.inventory_weight = weight
        runtime_bot.game_state.inventory.weight_max = 1000

        assert runtime_bot.game_state.inventory.is_full_pods is expected

    def test_kamas_update_event_sets_kamas(
        self,
        runtime_bot: Bot,
    ):
        runtime_bot.game_state.inventory.kamas = 1000

        runtime_bot.event_manager.process_msg(KamasUpdateEvent(quantity=700))

        assert runtime_bot.game_state.inventory.kamas == 700
