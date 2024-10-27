from dataclasses import dataclass, field
from functools import partial

from d3_mapping.resources.protos.game.common_pb2 import ObjectItemInventory
from d3_mapping.resources.protos.game.dialog_pb2 import DialogLeaveRequest
from d3_mapping.resources.protos.game.exchange_pb2 import (
    ExchangeLeaveEvent,
    ExchangeObjectMoveRequest,
)
from d3_mapping.resources.protos.game.guild_chest_pb2 import (
    GuildChestTabSelectRequest,
)
from d3_mapping.resources.protos.game.inventory_pb2 import (
    InventoryWeightEvent,
    StorageInventoryContentEvent,
)

from src.core.behaviors.behavior import Behavior
from src.core.behaviors.interactives.interactive_behavior import InteractiveBehavior
from src.core.behaviors.movements.auto_trip.auto_trip_smart_behavior import (
    AutoTripSmartBehavior,
)
from src.core.behaviors.storage.enter_chests.enter_guild_chest_behavior import (
    EnterGuildChestBehavior,
)
from src.core.config.timings import BASE_RANGE, SMALL_RANGE
from src.core.logic.map.path_finding.path_finding import Pathfinding


@dataclass
class UnloadInGuildChestBehavior(Behavior):
    interactive_behavior: InteractiveBehavior
    path_finding: Pathfinding
    auto_trip_world_behavior: AutoTripSmartBehavior
    enter_guild_chest_behavior: EnterGuildChestBehavior

    object_to_unload_on_tab: list[tuple[int, list[ObjectItemInventory]]] = field(
        init=False, default_factory=list
    )

    def run(self, unload_item_id_by_tab: dict[int, set[int]]):
        object_by_gid_in_inventory = {
            object.item.gid: object
            for object in self.game_state.inventory.objects_by_uid.values()
        }
        self.logger.info(
            f"Count objects in inventory : {len(object_by_gid_in_inventory)}"
        )

        self.object_to_unload_on_tab = []
        gids_treaded: set[int] = set()
        for tab, gids in unload_item_id_by_tab.items():
            object_to_unloads: list[ObjectItemInventory] = []
            for gid in gids:
                if (
                    object := object_by_gid_in_inventory.get(gid)
                ) and gid not in gids_treaded:
                    gids_treaded.add(gid)
                    object_to_unloads.append(object)
            if len(object_to_unloads) > 0:
                self.object_to_unload_on_tab.append((tab, object_to_unloads))

        self.logger.info(
            f"Count objects to unload on tabs  : {','.join([str(len(objects)) for _, objects in self.object_to_unload_on_tab])}"
        )
        if len(self.object_to_unload_on_tab) == 0:
            return self.finish()

        self.enter_guild_chest_behavior.start(
            callback=self.on_enter_guild_chest_behavior_finished, parent=self
        )

    def on_enter_guild_chest_behavior_finished(self, error_code: str | None):
        if error_code is not None:
            return self.finish(error_code)

        self.object_to_unload_on_tab = [
            (tab, objects)
            for tab, objects in self.object_to_unload_on_tab
            if tab in self.game_state.guild_chest.tabs
        ]
        self.logger.info(f"count tab to unload : {len(self.object_to_unload_on_tab)}")
        self.run_timer(BASE_RANGE, self.unload_tab)

    def unload_tab(self):
        if len(self.object_to_unload_on_tab) == 0:
            return self.run_timer(BASE_RANGE, self.on_all_unloaded)
        tab, object_to_unloads = self.object_to_unload_on_tab.pop()
        if tab != self.game_state.guild_chest.tab_number:
            self.event_manager.on(
                StorageInventoryContentEvent,
                partial(
                    self.on_storage_inventory_content_event,
                    object_to_unloads=object_to_unloads,
                ),
                once=True,
                originator=self,
            )
            return self.run_timer(
                SMALL_RANGE,
                lambda: self.event_manager.send(
                    GuildChestTabSelectRequest(tab_number=tab)
                ),
            )
        self.unload_object(object_to_unloads)

    def on_storage_inventory_content_event(
        self,
        msg: StorageInventoryContentEvent,
        object_to_unloads: list[ObjectItemInventory],
    ):
        self.run_timer(SMALL_RANGE, lambda: self.unload_object(object_to_unloads))

    def unload_object(self, object_to_unloads: list[ObjectItemInventory]):
        self.logger.info(f"Unloading objects : {object_to_unloads}")
        if len(object_to_unloads) == 0:
            return self.run_timer(BASE_RANGE, self.unload_tab)

        self.event_manager.on(
            InventoryWeightEvent,
            partial(
                self.on_inventory_weight_event, object_to_unloads=object_to_unloads
            ),
            originator=self,
            once=True,
        )
        next_object = object_to_unloads.pop()
        req = ExchangeObjectMoveRequest(
            object_uid=next_object.item.uid, quantity=next_object.item.quantity
        )
        self.event_manager.send(req)

    def on_inventory_weight_event(
        self, msg: InventoryWeightEvent, object_to_unloads: list[ObjectItemInventory]
    ):
        self.run_timer(SMALL_RANGE, lambda: self.unload_object(object_to_unloads))

    def on_all_unloaded(self):
        self.event_manager.on(
            ExchangeLeaveEvent,
            callback=lambda _: self.finish(),
            originator=self,
            once=True,
        )
        self.leave_all_dialogs()

    def leave_all_dialogs(self):
        request = DialogLeaveRequest()
        self.event_manager.send(request)
        self.event_manager.send(request)
