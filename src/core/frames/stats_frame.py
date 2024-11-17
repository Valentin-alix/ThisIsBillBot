from dataclasses import dataclass, field

from D3Database.data_center.data_reader import DataReader
from D3Database.data_center.i18n import I18N
from D3Mapping.d3_mapping.resources.protos.game.interactive_element_pb2 import (
    InteractiveUseRequest,
)
from D3Mapping.d3_mapping.resources.protos.game.inventory_pb2 import (
    ObjectAddedEvent,
    ObjectQuantityEvent,
)
from src.controller.farm_stats_controller import FarmStatsController
from src.core.events_manager.priority import PriorityEnum
from src.core.frames.frame import Frame


@dataclass
class StatsFrame(Frame):
    _inventory_snapshot: dict[int, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.event_manager.on(
            InteractiveUseRequest,
            self.on_interactive_use_request,
            self,
            priority=self.priority,
        )
        self.game_info_signals.fight_completed.connect(self.on_fight_completed)

    def on_interactive_use_request(self, _msg: InteractiveUseRequest):
        self._inventory_snapshot = {
            uid: obj.item.quantity
            for uid, obj in self.game_state.inventory.objects_by_uid.items()
        }

        with self.event_manager.lock:
            self.unregister_listener(ObjectAddedEvent)
            self.unregister_listener(ObjectQuantityEvent)
            self.event_manager.on(
                ObjectAddedEvent,
                self.on_object_added,
                self,
                priority=PriorityEnum.NORMAL,
            )
            self.event_manager.on(
                ObjectQuantityEvent,
                self.on_object_quantity,
                self,
                priority=PriorityEnum.NORMAL,
            )

    def on_object_added(self, msg: ObjectAddedEvent):
        self.unregister_listener(ObjectAddedEvent)
        self.unregister_listener(ObjectQuantityEvent)
        gid = msg.object.item.gid
        quantity_added = msg.object.item.quantity

        item = DataReader().item_by_id[gid]
        if not item.nameId:
            return

        resource_name = I18N().name_by_id[item.nameId]

        FarmStatsController().add_harvested_resource(
            self.game_state.player.character_name,
            resource_name,
            quantity_added,
        )
        self.game_info_signals.resource_harvested.emit(gid, quantity_added)

    def on_object_quantity(self, msg: ObjectQuantityEvent):
        self.unregister_listener(ObjectAddedEvent)
        self.unregister_listener(ObjectQuantityEvent)
        existing_obj = self.game_state.inventory.objects_by_uid.get(
            msg.object.object_uid
        )
        if not existing_obj:
            return

        gid = existing_obj.item.gid

        item = DataReader().item_by_id[gid]
        if not item.nameId:
            return

        resource_name = I18N().name_by_id[item.nameId]

        previous_quantity = self._inventory_snapshot.get(msg.object.object_uid, 0)
        quantity_added = msg.object.quantity - previous_quantity

        if quantity_added <= 0:
            return

        FarmStatsController().add_harvested_resource(
            self.game_state.player.character_name,
            resource_name,
            quantity_added,
        )
        self.game_info_signals.resource_harvested.emit(gid, quantity_added)

    def on_fight_completed(self, fight_count: int):
        FarmStatsController().add_fights(
            self.game_state.player.character_name, fight_count
        )
